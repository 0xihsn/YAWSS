/*  Copyright (C) 2020  IHSAN BILKAY

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>
*/


var previous_scan_results = null;

function fill_vuln_chart(data) {
    Chart.defaults.global.legend.display = false;
    let myChart = new Chart(document.getElementById("vuln-chart"), {
        type: 'doughnut',
        data: {
            labels: ["Info", "Low", "Medium", "High", "Critical"],
            datasets: [
                {
                    label: "Vulnerabilities",
                    backgroundColor: ["#5dade2", "#f7dc6f", "#eb984e", "#e74c3c", "#c71616"],
                    data: data
                }
            ]
        },
        options: {
            responsive: false,
            elements: {
                arc: {
                    borderWidth: 0
                }
            },
        }
    });
    // /* https://github.com/chartjs/Chart.js/issues/2292 */
    // document.getElementById("vuln-chart").onclick = function (evt) {
    //     let activePoints = myChart.getElementsAtEventForMode(evt, 'point', myChart.options);
    //     let firstPoint = activePoints[0];
    //     let label = myChart.data.labels[firstPoint._index];
    // };
}


function message(data) {
    let div = document.getElementById('message')
    div.innerHTML = data;
    $("#notification").toast('show');
}

function get_scan_details(name) {

    var cw = $('li').width();
    $('li').css({'height': cw + 'px'});

    let vuln_number = [0, 0, 0, 0, 0];
    let scan_res = document.getElementById('scan_res');
    $.post("data",
        {
            name: name,
        },
        function (data) {
            if (!Object.is(previous_scan_results, data)) {
                scan_res.innerText = '';
                previous_scan_results = data;
                let res = jQuery.parseJSON(data)
                if (res.done) {
                    stop_details_refresh();
                    document.getElementById(name).getElementsByClassName('scan-info').item(0).style.background = "#83C194";
                }

                // Set the counters values
                document.getElementById("links-num").innerHTML = Object.keys(res.links).length;
                document.getElementById("forms-num").innerText = res.forms.length;
                document.getElementById("queries-num").innerText = res.queries.length;
                document.getElementById("subdomain-num").innerText = res.subdomains.length;
                document.getElementById("files-num").innerText = res.files.length;

                // Add the vulnerabilities to the dashboard
                jQuery.each(res.vulnerabilities, function (i, val) {


                    let vuln_header_container = document.createElement('a')
                    vuln_header_container.classList.add('collapsed')
                    vuln_header_container.setAttribute('data-toggle', 'collapse')

                    let severity = document.createElement('div')
                    severity.classList.add(i);
                    severity.classList.add('severity')
                    severity.innerText = i;

                    let vuln_container = document.createElement('div')

                    jQuery.each(val, function (h, vuln_list) {

                        vuln_header_container.href = '.' + h;
                        vuln_container.setAttribute('class', 'collapse ' + h)
                        vuln_header_container.append(severity)

                        let module_name = document.createElement('div')
                        module_name.classList.add('module-name')
                        module_name.innerText = h

                        vuln_header_container.append(module_name)
                        $("#scan_res").append(vuln_header_container);

                        // Count the vulnerabilities to draw the chart
                        for (let vuln in vuln_list) {
                            switch (i) {
                                case "Info":
                                    vuln_number[0]++;
                                    break;
                                case "Low":
                                    vuln_number[1]++;
                                    break;
                                case "Medium":
                                    vuln_number[2]++;
                                    break;
                                case "High":
                                    vuln_number[3]++;
                                    break;
                                case "Critical":
                                    vuln_number[4]++;
                                    break;
                            }
                            vuln_header_container.href = '.' + h;
                            let vuln_div = document.createElement('div')
                            vuln_div.setAttribute('class', 'vuln')

                            var res = JSON.stringify(vuln_list[vuln]);
                            vuln_div.innerText = res;


                            vuln_container.append(vuln_div);
                            vuln_container.append(document.createElement('br'));
                        }
                    });
                    $("#scan_res").append(vuln_container)
                });

                let base_url = document.createElement('a')
                base_url.href = res.base_url
                base_url.text = res.base_url

                let target = document.getElementById('info-table-target')
                target.innerHTML = ''
                $('#info-table-scan-name').text(res.name.toUpperCase());
                target.appendChild(base_url)
                $('#info-table-date').text(new Date(Date.now()));
                $('#info-table-vuln').text(vuln_number.reduce((a, b) => a + b, 0))


                fill_vuln_chart(vuln_number)
                document.getElementById('Counters').style.visibility = "visible";
                document.getElementById('right-header').style.visibility = "visible";
            }
        });
}


function add_new_scan(name) {

    let exist = document.getElementById(name)
    if (exist) {
        return
    }
    let scans = document.getElementById('left-content')
    var scan_modules = [];
    $.each($("input[name='scan_module']:checked"), function () {
        scan_modules.push($(this).val());
    });
    let modules = scan_modules.join(',')
    let div = document.createElement('div');
    div.id = name;
    div.innerHTML = `
        <button class="scan-btn scan-info" onclick="scan_details_starter('${name}')">
            <span id="scan-name">${name}</span>
        </button>
        <button class="scan-ctrl" style="background: darkseagreen" onclick="start_scan('${name}','${modules}')">&#9654;</button>
        <button class="scan-ctrl" style="background: coral" onclick="stop_scan('${name}')">&#9724;</button>
        <button class="scan-ctrl" style="background: crimson" onclick="delete_element('${name}')">&#9940;</button>
    `
    scans.appendChild(div);
    save_the_scans_list();
}


function fill_the_new_scan_modal() {
    $.get("get_scans_and_modules_names", function (resp) {
        let data = jQuery.parseJSON(resp)
        let scan_names_object = document.getElementById('new-scan-name');
        scan_names_object.textContent = ''
        for (n in data.scans) {
            let option = document.createElement("option");
            option.value = data.scans[n];
            option.text = data.scans[n];
            scan_names_object.appendChild(option);
        }
        let modules_names_object = document.getElementById('new-scan-modals-names')
        modules_names_object.innerHTML = ''
        for (n in data.modules) {
            let input = document.createElement("input");
            input.type = 'checkbox';
            input.name = 'scan_module';
            input.value = data.modules[n];
            var text = document.createElement('span')
            text.innerHTML = "&nbsp;" + data.modules[n];
            modules_names_object.appendChild(input);
            modules_names_object.appendChild(text);
            modules_names_object.appendChild(document.createElement('br'))
        }
    });
}

function start_scan(name, modules) {
    document.getElementById(name).getElementsByClassName('scan-info').item(0).style.background = "#78a8ba"
    $.post("start_scan",
        {
            'name': name,
            'modules': modules
        },
        function (data) {
            message(data);
        });
    save_the_scans_list();
}

function stop_scan(name, msg = true) {
    document.getElementById(name).getElementsByClassName('scan-info').item(0).style.background = "#83969d"
    $.post("cancel_scan",
        {
            'name': name,
        },
        function (data) {
            if (msg) {
                message(data);
            }
        });
    save_the_scans_list();
    stop_details_refresh();
}

function reset_the_file_input() {
    $("#scan-file").val('');
    $("#module-file").val('');
}

function import_scan() {
    let myForm = $("#import-scan-form")[0]

    $.ajax({
        type: 'POST',
        url: '/add_scan',
        data: new FormData(myForm),
        processData: false,
        contentType: false,
        success: function (resp) {
            message(resp)
        }

    })
    reset_the_file_input();
}


function import_module() {
    let myForm = $("#import-module-form")[0]
    $.ajax({
        type: 'POST',
        url: '/add_module',
        data: new FormData(myForm),
        processData: false,
        contentType: false,
        success: function (resp) {
            message(resp)
        }
    })
    reset_the_file_input();
}

function delete_element(id) {
    stop_scan(id, false)
    message('Scan deleted.')
    document.getElementById(id).remove();
    save_the_scans_list();
    stop_details_refresh();
}


document.addEventListener("DOMContentLoaded", function (event) {
    $('#notification').toast({delay: 3000});
    document.getElementById('left-content').innerHTML = localStorage.getItem('scans')
    localStorage.setItem('scans', document.getElementById('left-content').innerHTML)
});


function save_the_scans_list() {
    localStorage.setItem('scans', document.getElementById('left-content').innerHTML)
}

var details_refresh_function = null;

function start_details_refresh(name) {
    get_scan_details(name)
    details_refresh_function = setInterval(function () {
        get_scan_details(name)
    }, 5000);
}


function stop_details_refresh() {
    clearInterval(details_refresh_function);
}

function scan_details_starter(name) {
    stop_details_refresh();
    start_details_refresh(name);
}