/* ==========================================================================
   QuickUtils API Directory — Main JavaScript
   Dark/Light mode toggle, mobile menu, smooth scrolling
   ========================================================================== */

(function () {
    'use strict';

    // ---------- Dark/Light Mode ----------
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }

    // Load saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const current = html.getAttribute('data-theme');
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    // ---------- Mobile Menu ----------
    const menuBtn = document.getElementById('mobile-menu-btn');
    const mainNav = document.getElementById('main-nav');

    if (menuBtn && mainNav) {
        menuBtn.addEventListener('click', function () {
            const isOpen = mainNav.classList.toggle('open');
            menuBtn.setAttribute('aria-expanded', isOpen);
        });

        // Close menu when clicking a nav link
        mainNav.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                mainNav.classList.remove('open');
                menuBtn.setAttribute('aria-expanded', 'false');
            });
        });
    }

    // ---------- Smooth Scroll for Anchor Links ----------
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    // ---------- World Clock ----------
    function updateWorldClocks() {
        var clocks = document.querySelectorAll('.clock-time[data-tz]');
        clocks.forEach(function (el) {
            try {
                var time = new Date().toLocaleTimeString('en-US', {
                    timeZone: el.getAttribute('data-tz'),
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: true
                });
                el.textContent = time;
            } catch (e) {
                el.textContent = '--:--';
            }
        });
    }

    if (document.querySelector('.clock-time')) {
        updateWorldClocks();
        setInterval(updateWorldClocks, 1000);
    }

    // ---------- Time Converter (Past / Future / Any Timezone) ----------
    var dtInput = document.getElementById('converter-datetime');
    var fromTzSelect = document.getElementById('converter-from-tz');
    var toTzSelect = document.getElementById('converter-to-tz');
    var fromDisplay = document.getElementById('converter-from-display');
    var toDisplay = document.getElementById('converter-to-display');
    var nowBtn = document.getElementById('converter-now-btn');

    function setDatetimeToNow() {
        if (!dtInput) return;
        var now = new Date();
        // Format as YYYY-MM-DDTHH:MM for datetime-local input
        var y = now.getFullYear();
        var m = String(now.getMonth() + 1).padStart(2, '0');
        var d = String(now.getDate()).padStart(2, '0');
        var h = String(now.getHours()).padStart(2, '0');
        var min = String(now.getMinutes()).padStart(2, '0');
        dtInput.value = y + '-' + m + '-' + d + 'T' + h + ':' + min;
    }

    function getOffsetMs(tz, refDate) {
        // Get the UTC offset in ms for a given timezone at a given date
        var fmt = new Intl.DateTimeFormat('en-US', {
            timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
        });
        var parts = {};
        fmt.formatToParts(refDate).forEach(function (p) { parts[p.type] = p.value; });
        var hr = parseInt(parts.hour, 10);
        if (hr === 24) hr = 0;
        var tzDate = new Date(
            parseInt(parts.year, 10), parseInt(parts.month, 10) - 1, parseInt(parts.day, 10),
            hr, parseInt(parts.minute, 10), parseInt(parts.second, 10)
        );
        return tzDate.getTime() - refDate.getTime();
    }

    function updateConverter() {
        if (!dtInput || !fromTzSelect || !toTzSelect || !fromDisplay || !toDisplay) return;
        if (!dtInput.value) { setDatetimeToNow(); }

        var inputDate = new Date(dtInput.value);
        if (isNaN(inputDate.getTime())) {
            fromDisplay.textContent = 'Invalid date';
            toDisplay.textContent = '--';
            return;
        }

        var fromTz = fromTzSelect.value;
        var toTz = toTzSelect.value;

        try {
            // The input is "wall clock" time in the FROM timezone.
            // We need to find the UTC instant, then display it in TO timezone.
            var utcInstant;
            if (fromTz === 'LOCAL') {
                utcInstant = inputDate;
            } else {
                // Convert from-tz wall time to UTC:
                // offset = how far fromTz is from UTC at that time
                var localOffset = getOffsetMs(fromTz, inputDate);
                utcInstant = new Date(inputDate.getTime() - localOffset);
                // Iteratively refine (offset may change near DST boundary)
                var refined = getOffsetMs(fromTz, utcInstant);
                utcInstant = new Date(inputDate.getTime() - refined);
            }

            var fmtOpts = {
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit', hour12: true
            };

            var fromStr = utcInstant.toLocaleString('en-US',
                Object.assign({}, fmtOpts, fromTz !== 'LOCAL' ? { timeZone: fromTz } : {})
            );
            var toStr = utcInstant.toLocaleString('en-US',
                Object.assign({}, fmtOpts, { timeZone: toTz })
            );

            fromDisplay.textContent = fromStr;
            toDisplay.textContent = toStr;
        } catch (e) {
            fromDisplay.textContent = '--';
            toDisplay.textContent = '--';
        }
    }

    if (dtInput) {
        setDatetimeToNow();
        updateConverter();
        dtInput.addEventListener('input', updateConverter);
        if (fromTzSelect) fromTzSelect.addEventListener('change', updateConverter);
        if (toTzSelect) toTzSelect.addEventListener('change', updateConverter);
        if (nowBtn) nowBtn.addEventListener('click', function () {
            setDatetimeToNow();
            updateConverter();
        });
    }

})();
