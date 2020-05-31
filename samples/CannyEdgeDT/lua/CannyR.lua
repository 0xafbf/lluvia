local builder = ll.class(ll.ComputeNodeBuilder)

function builder.newDescriptor()

	local desc = ll.ComputeNodeDescriptor.new()

	desc.builderName = 'CannyR'
	desc.localShape = ll.vec3ui.new(32, 32, 1)
	desc.gridShape = ll.vec3ui.new(1,1,1)
	desc.program = ll.getProgram('CannyR')
	desc.functionName = 'main'

	desc:addPort(ll.PortDescriptor.new(0, 'input_gradient', ll.PortDirection.In, ll.PortType.ImageView))
	desc:addPort(ll.PortDescriptor.new(1, 'output_image', ll.PortDirection.Out, ll.PortType.ImageView))

    desc:setParameter('texelWidth', 1)
    desc:setParameter('texelHeight', 1)
    desc:setParameter('upperThreshold', 100)
    desc:setParameter('lowerThreshold', 70)

	return desc
end

function builder.onNodeInit(node)


    local pushConstants = ll.PushConstants.new()
    pushConstants:pushFloat(node:getParameter('texelWidth'))
    pushConstants:pushFloat(node:getParameter('texelHeight'))
    pushConstants:pushFloat(node:getParameter('upperThreshold'))
    pushConstants:pushFloat(node:getParameter('lowerThreshold'))
    node.pushConstants = pushConstants



	local input_image = node:getPort('input_gradient')
	local memory = input_image.memory

	output_image = memory:createImageView(
		ll.ImageDescriptor.new(
			1, -- depth
			input_image.height, -- height
			input_image.width, -- width
			ll.ChannelCount.C1, -- channelCount
			ll.ChannelType.Float32 -- channelType
		),
		ll.ImageViewDescriptor.new(
			ll.ImageAddressMode.MirroredRepeat,
			ll.ImageFilterMode.Nearest,
			false, -- normalizedCoordinates
			false -- isSampled
		)
	)

	output_image:changeImageLayout(ll.ImageLayout.General)
    output_image:clear()

    node:bind('output_image', output_image)
    node:configureGridShape(ll.vec3ui.new(output_image.width, output_image.height, 1))

end

ll.registerNodeBuilder('CannyR', builder)


