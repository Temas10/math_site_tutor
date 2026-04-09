(function ($) {

  "use strict";

  $(document).ready(function () {

    $("#preloader").fadeOut("slow");

    // Поиск
    $(".user-items .search-item").click(function () {
      $(".search-box").toggleClass('active');
      $(".search-box .search-input").focus();
    });
    $(".close-button").click(function () {
      $(".search-box").toggleClass('active');
    });

    // Главный слайдер
    var swiper = new Swiper(".main-swiper", {
      speed: 800,
      loop: true,
      autoplay: { delay: 5000 },
      pagination: {
        el: "#billboard .swiper-pagination",
        clickable: true,
      },
    });

    // Слайдеры с карточками (тарифами)
    $('.product-swiper').each(function () {
      var sectionId = $(this).attr('id');
      var swiper = new Swiper("#" + sectionId + " .swiper", {
        slidesPerView: 4,
        spaceBetween: 20,
        pagination: {
          el: "#" + sectionId + " .swiper-pagination",
          clickable: true,
        },
        breakpoints: {
          0: { slidesPerView: 1, spaceBetween: 20 },
          768: { slidesPerView: 2, spaceBetween: 10 },
          999: { slidesPerView: 3, spaceBetween: 10 },
          1366: { slidesPerView: 4, spaceBetween: 40 },
        },
      });
    })

    // Слайдер отзывов
    var swiperTest = new Swiper(".testimonial-swiper", {
      loop: true,
      autoplay: { delay: 4000 },
      navigation: {
        nextEl: ".swiper-arrow-next",
        prevEl: ".swiper-arrow-prev",
      },
      pagination: {
        el: "#testimonials .swiper-pagination",
        clickable: true,
      },
    });

    // Sticky (если используется)
    if ($('.feat-swiper').length) {
      $('.feat-swiper').hcSticky({
        stickTo: $('.feat-product-grid')
      });
    }

  }); // End of a document

})(jQuery);

// Обработка форм через API
$(document).ready(function() {
    
    // Форма подписки
    $('#subscribe-form, #form').on('submit', function(e) {
        e.preventDefault();
        var email = $(this).find('input[type="email"]').val();
        
        $.ajax({
            url: '/api/subscribe',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email: email }),
            success: function(response) {
                alert('Спасибо за подписку!');
                $(e.target).trigger('reset');
            },
            error: function() {
                alert('Произошла ошибка. Попробуйте позже.');
            }
        });
    });
    
    // Форма записи на пробный урок
    $('#order-form').on('submit', function(e) {
        e.preventDefault();
        var formData = {
            name: $('#order-name').val(),
            email: $('#order-email').val(),
            phone: $('#order-phone').val(),
            program: $('#order-program').val(),
            preferred_date: $('#order-date').val(),
            comment: $('#order-comment').val()
        };
        
        $.ajax({
            url: '/api/order',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                alert('Заявка принята! Скоро с вами свяжутся.');
                $(e.target).trigger('reset');
                $('#orderModal').modal('hide');
            },
            error: function() {
                alert('Произошла ошибка. Попробуйте позже.');
            }
        });
    });
    
});

// ==================== Обработка форм через API ====================

$(document).ready(function() {
    
    // Форма подписки (в футере)
    $('#subscribe-form, #form').on('submit', function(e) {
        e.preventDefault();
        
        var emailInput = $(this).find('input[type="email"]');
        var email = emailInput.val();
        
        if (!email || email.indexOf('@') === -1) {
            alert('Пожалуйста, введите корректный email');
            return;
        }
        
        // Отправка на бэкенд
        $.ajax({
            url: '/api/subscribe',
            method: 'POST',
            data: { email: email },
            success: function(response) {
                alert(response.message || 'Спасибо за подписку!');
                emailInput.val(''); // Очищаем поле
            },
            error: function() {
                alert('Произошла ошибка. Попробуйте позже.');
            }
        });
    });
    
    // Кнопки "Записаться" и "Пробный урок"
    $('.btn-primary, .btn-outline-dark, .nav-link[href="#"]').on('click', function(e) {
        var text = $(this).text().toLowerCase();
        
        if (text.includes('записаться') || text.includes('пробный') || text.includes('подробнее')) {
            e.preventDefault();
            showOrderModal();
        }
    });
    
});

// Функция показа модального окна записи
function showOrderModal() {
    var modalHtml = `
        <div class="modal fade" id="orderModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Запись на пробный урок</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="order-form">
                            <div class="mb-3">
                                <input type="text" class="form-control" name="name" placeholder="Ваше имя" required>
                            </div>
                            <div class="mb-3">
                                <input type="email" class="form-control" name="email" placeholder="Email" required>
                            </div>
                            <div class="mb-3">
                                <input type="tel" class="form-control" name="phone" placeholder="Телефон" required>
                            </div>
                            <div class="mb-3">
                                <select class="form-control" name="program" required>
                                    <option value="">Выберите программу</option>
                                    <option value="ОГЭ">Подготовка к ОГЭ</option>
                                    <option value="ЕГЭ">Подготовка к ЕГЭ</option>
                                    <option value="Онлайн">Онлайн занятия</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <input type="date" class="form-control" name="preferred_date">
                            </div>
                            <div class="mb-3">
                                <textarea class="form-control" name="comment" rows="3" placeholder="Комментарий"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Отправить заявку</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Удаляем старую модалку если есть
    $('#orderModal').remove();
    
    // Добавляем новую
    $('body').append(modalHtml);
    
    // Показываем
    var modal = new bootstrap.Modal(document.getElementById('orderModal'));
    modal.show();
    
    // Обработчик отправки формы
    $('#order-form').on('submit', function(e) {
        e.preventDefault();
        
        var formData = {
            name: $(this).find('[name="name"]').val(),
            email: $(this).find('[name="email"]').val(),
            phone: $(this).find('[name="phone"]').val(),
            program: $(this).find('[name="program"]').val(),
            preferred_date: $(this).find('[name="preferred_date"]').val(),
            comment: $(this).find('[name="comment"]').val()
        };
        
        $.ajax({
            url: '/api/order',
            method: 'POST',
            data: formData,
            success: function(response) {
                alert(response.message);
                modal.hide();
                $('#order-form')[0].reset();
            },
            error: function() {
                alert('Ошибка при отправке. Попробуйте позже.');
            }
        });
    });
}