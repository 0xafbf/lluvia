local builder = ll.class(ll.ComputeNodeBuilder)

function builder.newDescriptor()

	local desc = ll.ComputeNodeDescriptor.new()

	desc.builderName = 'LineDetect'
	desc.localShape = ll.vec3ui.new(32, 32, 1)
	desc.gridShape = ll.vec3ui.new(1,1,1)
	desc.program = ll.getProgram('LineDetect')
	desc.functionName = 'main'

	desc:addPort(ll.PortDescriptor.new(0, 'input_image', ll.PortDirection.In, ll.PortType.ImageView))
	desc:addPort(ll.PortDescriptor.new(1, 'output_image', ll.PortDirection.Out, ll.PortType.ImageView))

    desc:setParameter('scale', 20)

	return desc
end

function builder.onNodeInit(node)

    ll.logd('LineDetect', 'setting push constants')

    local pushConstants = ll.PushConstants.new()
    pushConstants:pushFloat(node:getParameter('scale'))
    node.pushConstants = pushConstants

	local input_image = node:getPort('input_image')

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

ll.registerNodeBuilder('LineDetect', builder)




