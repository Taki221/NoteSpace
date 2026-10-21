document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("loginForm");
    
    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault(); // Отменяем стандартную отправку формы
            
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const submitBtn = loginForm.querySelector(".login-button");

            submitBtn.disabled = true;
            submitBtn.textContent = "Вход...";

            try {
                const response = await fetch("/api/login/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username: username, password: password }),
                    credentials: "include"
                });

                if (response.ok) {
                    window.location.href = "/notes/"; // Редирект на нашу страницу заметок
                } else {
                    alert("Неверный логин или пароль");
                }
            } catch (error) {
                console.error(error);
                alert("Ошибка сервера");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = "Войти";
            }
        });
    }
});