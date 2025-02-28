$(document).ready(function () {
    // File search autocomplete
    $("#file-search").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/search",
                data: { q: request.term },
                success: function (data) {
                    response(data);
                },
                error: function () {
                    console.error("Error fetching autocomplete data");
                },
            });
        },
        minLength: 2,
        select: function (event, ui) {
            addFileToList(ui.item.value);
            $("#file-search").val('');
            return false;
        },
    });

    // Add file when pressing Enter
    $("#file-search").on("keydown", function (event) {
        if (event.key === "Enter") {
            const fileName = $(this).val().trim();
            if (fileName) {
                addFileToList(fileName);
                $(this).val('');
            }
            event.preventDefault();
        }
    });

    // Add file to the list
    function addFileToList(fileName) {
        const fileList = $("#file-list");
        const fileId = `file-${Date.now()}`;
        const fileItem = `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="${fileId}" value="${fileName}" checked>
                <label class="form-check-label" for="${fileId}">${fileName}</label>
            </div>`;
        fileList.append(fileItem);
    }

    // Launch OpenOCD
    $("#launch-openocd").on("click", function () {
        const selectedFiles = [];
        $("#file-list input:checked").each(function () {
            selectedFiles.push($(this).val());
        });

        if (selectedFiles.length === 0) {
            alert("Please select at least one file to launch OpenOCD.");
            return;
        }

        $.ajax({
            url: "/launch_openocd",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ files: selectedFiles }),
            success: function (response) {
                if (response.status === "success") {
                    $("#openocd-output").text(response.message + "\n" + response.output);
                } else {
                    $("#openocd-output").text(response.message);
                }
            },
            error: function (xhr) {
                $("#openocd-output").text("Error: " + xhr.responseJSON.message);
            },
        });
    });
});
