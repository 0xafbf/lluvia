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

    glslPath = os.path.join(lluviaBasePath, 'bazel-bin/samples/SobelEdgeDT/glsl')
    luaPath = os.path.join(lluviaBasePath, 'samples/SobelEdgeDT/lua')

    util = importlib.import_module('lluvia.util')
    util.loadNodes(session, glslPath, luaPath)

    memory = session.createMemory()


    desc = session.createComputeNodeDescriptor('LineDetect')

    lineDetect = session.createComputeNode(desc)
    scale_param = ll.Parameter(10)
    lineDetect.setParameter('scale', scale_param)



    cap = cv.VideoCapture(args.input_file)
    r, img = cap.read()

    RGBA = cv.cvtColor(img, cv.COLOR_BGR2RGBA)

    img_gpu =  memory.createImageFromHost(RGBA).createImageView()
    lineDetect.bind('input_image',img_gpu)
    lineDetect.init()

    push_constants = lineDetect.getPushConstants()

    duration = session.createDuration()

    cmdBuffer = session.createCommandBuffer()

    def fill_cmd_buffer(cmdBuffer):
        cmdBuffer.begin()
        cmdBuffer.durationStart(duration)
        lineDetect.record(cmdBuffer)
        cmdBuffer.memoryBarrier()
        cmdBuffer.durationEnd(duration)
        cmdBuffer.run(lineDetect)
        cmdBuffer.end()

    fill_cmd_buffer(cmdBuffer)

    width = img_gpu.width
    height = img_gpu.height

    def on_trackbar(val):
        val_sq = val * val
        scale_param.set(val_sq)
        push_constants.set(float(val_sq))
        lineDetect.setPushConstants(push_constants)
        fill_cmd_buffer(cmdBuffer)


    cv.namedWindow("my window")
    cv.createTrackbar("my trackbar", "my window", 1, 30, on_trackbar)


    while r:

        r, img = cap.read()
        if not r:
            break

        RGBA = cv.cvtColor(img, cv.COLOR_BGR2RGBA)

        img_gpu.fromHost(RGBA)
        session.run(cmdBuffer)
        result = lineDetect.getPort('output_image').toHost()

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

