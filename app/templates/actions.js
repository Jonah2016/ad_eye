// On submit send request for detection task
    async function executeDetectionAction(form_data, dis)
    {
        await fetch('/process_jobs_status_actions', {
            method: 'POST',
            body: form_data,
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.status === 200) {
                if (data.url) {window.location.href = data.url; }
                else {success_operation(data.msg);}

                if ($('#queuedJobsList').length > 0) {location.reload();} // when the page is query and id is detected
                $(dis).prop("disabled",false);
            } else {
                error_operation(data.msg);
                $(dis).prop("disabled",false);
            }
        })
        .catch(err => {
            error_operation('E0x0000000JxDETECTION_PROCESS: SYSTEM_ERROR_OCCURRED');
            $(dis).prop("disabled",false);
        })
    }

    function clickActionBtnQuery(dis) {
        $(dis).prop("disabled",true);

        const job_id = dis.dataset.job_id;
        const action = dis.dataset.action;
        const job_type = dis.dataset.job_type;
        const job_mode = dis.dataset.job_mode;

        if (job_id == "" || job_id == null || job_id == undefined) {
            error_operation("Action could not be executed. Refresh the page and try again.");
            return false;
        }
        if (action == "" || action == null || action == undefined) {
            error_operation("Action could not be executed. Refresh the page and try again.");
            return false;
        }

        let formData = new FormData();
        formData.append('job_id', job_id);
        formData.append('action', action);
        formData.append('job_type', job_type);
        formData.append('job_mode', job_mode);
        // parse form for action
        executeDetectionAction(formData, dis);
    }