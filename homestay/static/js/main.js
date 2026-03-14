// ── NAVBAR SCROLL EFFECT ──
const nav = document.getElementById('mainNav');
if (nav) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });
}

// ── WEATHER WIDGET ──
async function fetchWeather() {
    const lat = 30.1326;
    const lon = 78.3240;
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&wind_speed_unit=kmh&timezone=Asia%2FKolkata`;

    const weatherDescriptions = {
        0: { label: 'Clear Sky', icon: '☀️' },
        1: { label: 'Mainly Clear', icon: '🌤️' },
        2: { label: 'Partly Cloudy', icon: '⛅' },
        3: { label: 'Overcast', icon: '☁️' },
        45: { label: 'Foggy', icon: '🌫️' },
        48: { label: 'Icy Fog', icon: '🌫️' },
        51: { label: 'Light Drizzle', icon: '🌦️' },
        53: { label: 'Drizzle', icon: '🌦️' },
        55: { label: 'Heavy Drizzle', icon: '🌧️' },
        61: { label: 'Light Rain', icon: '🌧️' },
        63: { label: 'Rain', icon: '🌧️' },
        65: { label: 'Heavy Rain', icon: '🌧️' },
        71: { label: 'Light Snow', icon: '🌨️' },
        73: { label: 'Snow', icon: '❄️' },
        75: { label: 'Heavy Snow', icon: '❄️' },
        80: { label: 'Rain Showers', icon: '🌦️' },
        81: { label: 'Rain Showers', icon: '🌦️' },
        82: { label: 'Heavy Showers', icon: '⛈️' },
        95: { label: 'Thunderstorm', icon: '⛈️' },
        96: { label: 'Thunderstorm with Hail', icon: '⛈️' },
        99: { label: 'Thunderstorm with Hail', icon: '⛈️' },
    };

    try {
        const response = await fetch(url);
        const data = await response.json();
        const current = data.current;

        const code = current.weather_code;
        const weatherInfo = weatherDescriptions[code] || { label: 'Partly Cloudy', icon: '🌤️' };

        const tempEl = document.getElementById('weatherTemp');
        const descEl = document.getElementById('weatherDesc');
        const iconEl = document.getElementById('weatherIcon');
        const humidityEl = document.getElementById('weatherHumidity');
        const windEl = document.getElementById('weatherWind');
        const feelsLikeEl = document.getElementById('weatherFeelsLike');

        if (tempEl) tempEl.textContent = `${Math.round(current.temperature_2m)}°C`;
        if (descEl) descEl.textContent = weatherInfo.label;
        if (iconEl) iconEl.innerHTML = `<span style="font-size: 2.8rem;">${weatherInfo.icon}</span>`;
        if (humidityEl) humidityEl.textContent = `${current.relative_humidity_2m}%`;
        if (windEl) windEl.textContent = `${Math.round(current.wind_speed_10m)} km/h`;
        if (feelsLikeEl) feelsLikeEl.textContent = `${Math.round(current.apparent_temperature)}°C`;

    } catch (err) {
        const descEl = document.getElementById('weatherDesc');
        if (descEl) descEl.textContent = 'Weather unavailable';
        const tempEl = document.getElementById('weatherTemp');
        if (tempEl) tempEl.textContent = '--°C';
    }
}

if (document.getElementById('weatherWidget')) {
    fetchWeather();
}

// ── SCROLL FADE-IN ANIMATION ──
const fadeElements = document.querySelectorAll('.fade-in');

function checkFadeIn() {
    const triggerBottom = window.innerHeight * 0.9;
    fadeElements.forEach(el => {
        const top = el.getBoundingClientRect().top;
        if (top < triggerBottom) {
            el.classList.add('visible');
        }
    });
}

if (fadeElements.length > 0) {
    window.addEventListener('scroll', checkFadeIn);
    checkFadeIn();
}

// ── SET MIN DATE FOR DATE INPUTS ──
document.querySelectorAll('input[type="date"]').forEach(input => {
    const today = new Date().toISOString().split('T')[0];
    input.setAttribute('min', today);
});

// ── CHECK-OUT MIN DATE ──
const checkInInputs = document.querySelectorAll('input[name="check_in"]');
const checkOutInputs = document.querySelectorAll('input[name="check_out"]');

checkInInputs.forEach((checkIn, i) => {
    checkIn.addEventListener('change', function () {
        if (checkOutInputs[i]) {
            checkOutInputs[i].setAttribute('min', this.value);
            if (checkOutInputs[i].value && checkOutInputs[i].value < this.value) {
                checkOutInputs[i].value = '';
            }
        }
    });
});

// ── IMAGE PREVIEW ON FILE INPUT ──
document.querySelectorAll('input[type="file"][accept*="image"]').forEach(input => {
    input.addEventListener('change', function () {
        const preview = this.parentElement.querySelector('.img-preview');
        if (preview && this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = e => { preview.src = e.target.result; preview.style.display = 'block'; };
            reader.readAsDataURL(this.files[0]);
        }
    });
});

// ── ACTIVE NAV LINK ──
const currentPath = window.location.pathname;
document.querySelectorAll('#mainNav .nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
    }
});
