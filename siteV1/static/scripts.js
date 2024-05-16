document.addEventListener('DOMContentLoaded', () => {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];

    // Функция для обновления корзины
    function updateCart() {
        const cartItems = document.getElementById('cart-items');
        const totalPriceElement = document.getElementById('total-price');

        if (cartItems && totalPriceElement) {
            cartItems.innerHTML = '';
            let total = 0;

            if (cart.length === 0) {
                cartItems.innerHTML = '<p>Ваша корзина пуста.</p>';
                totalPriceElement.textContent = 'Итоговая сумма: 0₽';
            } else {
                cart.forEach(item => {
                    const itemElement = document.createElement('div');
                    itemElement.classList.add('cart-item');
                    itemElement.innerHTML = `<p>${item.name} (${item.quantity} шт): ${item.price * item.quantity}₽</p>
                        <button class="remove-item" data-id="${item.id}">Удалить</button>`;
                    cartItems.appendChild(itemElement);
                    total += parseFloat(item.price) * item.quantity;
                });
                totalPriceElement.textContent = `Итоговая сумма: ${total}₽`;
            }

            localStorage.setItem('cart', JSON.stringify(cart));
        }
    }

    const buttons = document.querySelectorAll('button[data-id]');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            const price = button.getAttribute('data-price');
            const quantityInput = document.getElementById(`quantity-${id}`);
            const quantity = parseInt(quantityInput.value, 10);

            const existingItem = cart.find(item => item.id === id);

            if (existingItem) {
                alert('Этот товар уже в корзине!');
            } else {
                cart.push({ id, name, price, quantity });
                updateCart();
                alert('Товар добавлен в корзину!');
            }
        });
    });

    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-item')) {
            const id = e.target.getAttribute('data-id');
            cart = cart.filter(item => item.id !== id);
            updateCart();
        }
    });

    const clearCartButton = document.getElementById('clear-cart');
    if (clearCartButton) {
        clearCartButton.addEventListener('click', () => {
            cart = [];
            updateCart();
        });
    }

    const checkoutButton = document.getElementById('checkout');
    if (checkoutButton) {
        checkoutButton.addEventListener('click', () => {
            window.location.href = '/checkout';
        });
    }

    updateCart();

    // Функция для фильтрации товаров
    function filterItems() {
        const countryFilter = document.getElementById('country-filter').value;
        const yearFilter = parseInt(document.getElementById('year-filter').value, 10);
        const priceFilter = parseFloat(document.getElementById('price-filter').value);

        const coins = document.querySelectorAll('.coin');
        coins.forEach(coin => {
            const coinCountry = coin.getAttribute('data-country');
            const coinYear = parseInt(coin.getAttribute('data-year'), 10);
            const coinPrice = parseFloat(coin.getAttribute('data-price'));

            let show = true;

            if (countryFilter && countryFilter !== coinCountry) {
                show = false;
            }

            if (!isNaN(yearFilter) && coinYear !== yearFilter) {
                show = false;
            }

            if (!isNaN(priceFilter) && coinPrice > priceFilter) {
                show = false;
            }

            coin.style.display = show ? '' : 'none';
        });
    }

    // Добавление обработчика для кнопки фильтрации
    document.getElementById('filter-btn').addEventListener('click', filterItems);
});
