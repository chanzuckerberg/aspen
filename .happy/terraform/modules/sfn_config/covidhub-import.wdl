version 1.1

workflow covidhub_import {
    input {
        String docker_image_id = "covidhub-import"
        String aws_region = "us-west-2"
    }

    call covidhub_import_workflow {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
    }
}

task covidhub_import_workflow {
    input {
        String docker_image_id
        String aws_region
    }

    command <<<
    aspen-cli db --remote import-covidhub-users --covidhub-db-secret 'covidhub-staging-db' --rr-project-id 'RR066e'
    >>>

    runtime {
        docker: docker_image_id
    }
}

