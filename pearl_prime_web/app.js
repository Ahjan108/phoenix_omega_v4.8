(function () {
  'use strict';

  var CONFIG_URL = 'config/pearl_prime/ticker_phrases.json';
  var FALLBACK = {
    schema_version: '1.0',
    ticker: {
      en: [
        'Spread wisdom to every heart.',
        'Offer hope to the weary.',
        'Let the truth shine everywhere.',
        'Guide spirits toward freedom.',
        'Carry compassion to the world.',
        'Lift hearts with words.',
        'Awaken the light within all.',
        'Share words of healing.',
        'Open paths to inner peace.',
        'Plant seeds of awakening.',
        'Bring clarity to the confused.',
        'Let wisdom flow to all beings.'
      ]
    },
    runner: {
      en: [
        'Books that inspire courage',
        'Books that awaken wisdom',
        'Stories that open hearts',
        'Stories that reveal truth',
        'Teachings that guide the path',
        'Teachings that bring clarity',
        'Exercises that calm the mind',
        'Exercises that restore balance',
        'Practices that nurture peace',
        'Practices that build resilience',
        'Words that uplift the spirit',
        'Words that spark transformation'
      ]
    }
  };

  function getTickerPhrases(config) {
    return (config && config.ticker && config.ticker.en && config.ticker.en.length)
      ? config.ticker.en
      : FALLBACK.ticker.en;
  }

  function getRunnerPhrases(config) {
    return (config && config.runner && config.runner.en && config.runner.en.length)
      ? config.runner.en
      : FALLBACK.runner.en;
  }

  function buildTickerDOM(phrases) {
    var sep = '\u00A0\u2022\u00A0';
    var parts = phrases.slice();
    parts.push.apply(parts, phrases);
    var fragment = document.createDocumentFragment();
    for (var i = 0; i < parts.length; i++) {
      var span = document.createElement('span');
      span.className = 'ticker-phrase';
      span.textContent = parts[i];
      fragment.appendChild(span);
      if (i < parts.length - 1) {
        var s = document.createElement('span');
        s.className = 'ticker-sep';
        s.textContent = sep;
        fragment.appendChild(s);
      }
    }
    return fragment;
  }

  function buildRunnerDOM(phrases) {
    var doubled = phrases.slice();
    doubled.push.apply(doubled, phrases);
    var fragment = document.createDocumentFragment();
    for (var i = 0; i < doubled.length; i++) {
      var div = document.createElement('div');
      div.className = 'runner-phrase';
      div.textContent = doubled[i];
      fragment.appendChild(div);
    }
    return fragment;
  }

  function run() {
    var tickerEl = document.getElementById('ticker-track');
    var runnerEl = document.getElementById('runner-track');
    if (!tickerEl || !runnerEl) return;

    function applyConfig(config) {
      var tickerPhrases = getTickerPhrases(config);
      var runnerPhrases = getRunnerPhrases(config);
      tickerEl.innerHTML = '';
      runnerEl.innerHTML = '';
      tickerEl.appendChild(buildTickerDOM(tickerPhrases));
      runnerEl.appendChild(buildRunnerDOM(runnerPhrases));
    }

    fetch(CONFIG_URL)
      .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(applyConfig)
      .catch(function () { applyConfig(FALLBACK); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
