pipelineJob('BusVoodoo_dev') {
    definition {
        cps {
            script(readFileFromWorkspace('BusVoodoo.groovy'))
            sandbox()
        }
    }
}
