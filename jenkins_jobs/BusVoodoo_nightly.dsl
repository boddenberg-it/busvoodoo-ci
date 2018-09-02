pipelineJob('BusVoodoo_nightly') {
    definition {
        cps {
            script(readFileFromWorkspace('BusVoodoo_nightly.groovy'))
            sandbox()
        }
    }
}
