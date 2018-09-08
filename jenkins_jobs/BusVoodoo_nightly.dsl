pipelineJob('BusVoodoo_nightly') {
    definition {
        blockOn('')
        checkoutRetryCount(3)
        concurrentBuild(false)
        description('')
        logRotator(-1, 50, -1, 100)
        trigger{
          scm(00 11,10 * * *)
        }

        cps {
            script(readFileFromWorkspace('busvoodoo-ci/jenkins_jobs/BusVoodoo.groovy'))
            sandbox()
        }
    }
}
