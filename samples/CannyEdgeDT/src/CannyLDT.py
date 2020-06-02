#Idea de implementacion de codigo para SOB utilizando el motor grafico Lluvia

import argparse
import importlib
import os
import sys

import cv2 as cv


def main():

    # LOAD LLUVIA LIBRARY
    lluviaBasePath = None
    try:
        lluviaBasePath = os.environ['LL_PATH']
    except KeyError:
        print('Error reading LL_PATH environ variable')
        exit(-1)

    sys.path.append(os.path.join(
        # lluviaBasePath, 'build/python/lib.linux-x86_64-3.6'))
        lluviaBasePath, 'python/src'))

    pythonPath = os.path.join(lluviaBasePath, 'build/python/lib.linux-x86_64-3.6')
    pythonPath = os.path.join(lluviaBasePath, 'build/python/lib.win-amd64-3.8')

    sys.path.append(pythonPath)

    # PARSE ARGUMENTS
    parser = argparse.ArgumentParser(description='Optical flow filter.')
    parser.add_argument('input_file', type=str,
                        help='input video file path.')
    args = parser.parse_args()


    # INIT LLUVIA LIBRARY

    ll = importlib.import_module('lluvia')
    session = ll.createSession()

    glslPath = os.path.join(lluviaBasePath, 'bazel-bin/samples/CannyEdgeDT/glsl')
    luaPath = os.path.join(lluviaBasePath, 'samples/CannyEdgeDT/lua')

    util = importlib.import_module('lluvia.util')
    util.loadNodes(session, glslPath, luaPath)

    memory = session.createMemory()



    desc = session.createComputeNodeDescriptor('CannyLDT')
    cannyDetect = session.createComputeNode(desc)

    desc = session.createComputeNodeDescriptor('CannyR')
    cannyR = session.createComputeNode(desc)


    cap = cv.VideoCapture(args.input_file)
    r, img = cap.read()

    RGBA = cv.cvtColor(img, cv.COLOR_BGR2RGBA)

    img_gpu =  memory.createImageFromHost(RGBA).createImageView()
    cannyDetect.bind('input_image',img_gpu)

    cannyDetect.init()

    cannyR.bind('input_gradient', cannyDetect.getPort('output_image'))

    cannyR.init()

    duration = session.createDuration()

    cmdBuffer = session.createCommandBuffer()
    def fill_cmd_buffer(cmdBuffer):
        cmdBuffer.begin()
        cmdBuffer.durationStart(duration)
        cannyDetect.record(cmdBuffer)
        cannyR.record(cmdBuffer)
        cmdBuffer.memoryBarrier()
        cmdBuffer.durationEnd(duration)
        cmdBuffer.run(cannyR)
        cmdBuffer.end()

    fill_cmd_buffer(cmdBuffer);
    width = img_gpu.width
    height = img_gpu.height



    params = {}
    params['texelWidth'] = 1.0
    params['texelHeight'] = 1.0
    params['upperThreshold'] = 100.0
    params['lowerThreshold'] = 70.0

    def update_value(id, value):
        params[id] = float(value)
        send_push_constants()

    push_constants = cannyR.getPushConstants()
    def send_push_constants():
        push_constants.set(params['texelWidth'])
        push_constants.push(params['texelHeight'])
        push_constants.push(params['upperThreshold'])
        push_constants.push(params['lowerThreshold'])
        cannyR.setPushConstants(push_constants)
        fill_cmd_buffer(cmdBuffer)


    cv.namedWindow("my window")
    cv.createTrackbar("texel width", "my window", 1, 30, lambda x: update_value('texelWidth', x))
    cv.createTrackbar("texel height", "my window", 1, 30, lambda x: update_value('texelHeight', x))
    cv.createTrackbar("upperThreshold", "my window", 1, 255, lambda x: update_value('upperThreshold', x))
    cv.createTrackbar("lowerThreshold", "my window", 1, 255, lambda x: update_value('lowerThreshold', x))



    while r:

        r, img = cap.read()
        if not r:
            break

        RGBA = cv.cvtColor(img, cv.COLOR_BGR2RGBA)

        img_gpu.fromHost(RGBA)
        session.run(cmdBuffer)
        result = cannyR.getPort('output_image').toHost()

        ms = duration.nanoseconds * 1e-6

        img = cv.putText(img, '{0:.03f} ms'.format(ms),
                          (width - 200, 30),
                          cv.FONT_HERSHEY_SIMPLEX,
                          fontScale=1, color=(0, 0, 255), thickness=2)

        result = cv.putText(result, '{0:.03f} ms'.format(ms),
                              (width - 200, 30),
                              cv.FONT_HERSHEY_SIMPLEX,
                              fontScale=1, color=(0, 0, 255), thickness=2)

        cv.imshow('img', img)
        cv.imshow('flow', result)
        cv.waitKey(1)


if __name__ == '__main__':
    main()

