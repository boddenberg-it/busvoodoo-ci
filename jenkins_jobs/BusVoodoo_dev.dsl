pipelineJob('BusVoodoo_dev') {
    definition {
        blockOn('')
        checkoutRetryCount(3)
        concurrentBuild(false)
        description('')
        logRotator(-1, 50, -1, 100)

        stringParam(String GIT_BRANCH, String defaultValue = 'busvoodoo', String description = 'branch to build and test against')

        cps {
            script(readFileFromWorkspace('busvoodoo-ci/jenkins_jobs/BusVoodoo.groovy'))
            sandbox()
        }
    }
}
