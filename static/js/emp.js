
    let editingRow = null;

    function validateForm(event) {
        event.preventDefault();

        let isValid = true;

        const firstName = document.getElementById("firstName").value.trim();
        const lastName = document.getElementById("lastName").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const perfil = document.getElementById("perfil").value.trim();

        // Limpiar errores anteriores
        document.querySelectorAll(".error").forEach(el => el.textContent = "");

        if (firstName === "") {
            document.getElementById("firstNameError").textContent = "Nombre requerido";
            isValid = false;
        }
        if (lastName === "") {
            document.getElementById("lastNameError").textContent = "Apellido requerido";
            isValid = false;
        }
        if (!/^\d{10}$/.test(phone)) {
            document.getElementById("phoneError").textContent = "Teléfono inválido (10 dígitos)";
            isValid = false;
        }
        if (perfil === "") {
            document.getElementById("perfilError").textContent = "Perfil requerido";
            isValid = false;
        }

        if (isValid) {
            if (editingRow) {
                updateClient(editingRow);
            } else {
                addClient();
            }
            document.getElementById("employeeForm").reset();
            editingRow = null;
        }

        return false;
    }

    function addClient() {
        const table = document.getElementById("clientTable").getElementsByTagName("tbody")[0];
        const row = table.insertRow();

        row.innerHTML = `
            <td>${document.getElementById("firstName").value}</td>
            <td>${document.getElementById("lastName").value}</td>
            <td>${document.getElementById("phone").value}</td>
            <td>${document.getElementById("perfil").value}</td>
            <td>
                <button onclick="editClient(this)">Editar</button>
                <button onclick="deleteClient(this)">Eliminar</button>
            </td>
            
        `;
    }

    function editClient(button) {
        editingRow = button.parentElement.parentElement;

        document.getElementById("firstName").value = editingRow.cells[0].textContent;
        document.getElementById("lastName").value = editingRow.cells[1].textContent;
        document.getElementById("phone").value = editingRow.cells[2].textContent;
        document.getElementById("perfil").value = editingRow.cells[3].textContent;
    }

    function updateClient(row) {
        row.cells[0].textContent = document.getElementById("firstName").value;
        row.cells[1].textContent = document.getElementById("lastName").value;
        row.cells[2].textContent = document.getElementById("phone").value;
        row.cells[3].textContent = document.getElementById("perfil").value;
    }

    function deleteClient(button) {
        const row = button.parentElement.parentElement;
        row.remove();
    }
