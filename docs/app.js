const navigation = document.querySelector('.site-header nav');

const ensureHotTipsLink = () => {
  if (!navigation || navigation.querySelector('a[href="hot-tips.html"]')) return;

  const link = document.createElement('a');
  link.href = 'hot-tips.html';
  link.textContent = 'Hot Tips';
  if (window.location.pathname.endsWith('/hot-tips.html')) {
    link.setAttribute('aria-current', 'page');
  }

  const githubLink = navigation.querySelector('a[href*="github.com/oloix888/Personal-AI-Workspace"]');
  navigation.insertBefore(link, githubLink || null);
};

ensureHotTipsLink();

const menuButton = document.querySelector('.nav-toggle');
menuButton?.addEventListener('click', () => {
  const open = navigation?.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(Boolean(open)));
});

navigation?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navigation.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
  });
});

const createBrandLogo = (symbol, label, className, extraClass = '') => {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', label);
  svg.classList.add('brand-logo-svg', `brand-${className}`);
  if (extraClass) svg.classList.add(extraClass);

  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
  use.setAttribute('href', `assets/brand-logos.svg#${symbol}`);
  svg.appendChild(use);
  return svg;
};

const localizeBrandMarks = () => {
  const openAiPanel = document.querySelector('.platform-logo-pair');
  if (openAiPanel) {
    openAiPanel.classList.remove('required-artwork');
    openAiPanel.classList.add('required-brand-panel', 'openai-panel');
    openAiPanel.innerHTML = '';
    openAiPanel.appendChild(createBrandLogo('openai', 'OpenAI', 'openai', 'required-brand-svg'));

    const name = document.createElement('span');
    name.className = 'required-brand-name';
    name.innerHTML = '<strong>ChatGPT</strong><small>or Codex</small>';
    openAiPanel.appendChild(name);
  }

  const notionPanel = document.querySelector('.platform-logo-single');
  if (notionPanel) {
    notionPanel.classList.remove('required-artwork');
    notionPanel.classList.add('required-brand-panel', 'notion-panel');
    notionPanel.innerHTML = '';
    notionPanel.appendChild(createBrandLogo('notion', 'Notion', 'notion', 'required-brand-svg'));

    const name = document.createElement('span');
    name.className = 'required-brand-name';
    name.innerHTML = '<strong>Notion</strong><small>Your durable workspace</small>';
    notionPanel.appendChild(name);
  }

  const logoConfig = {
    Gmail: ['gmail', 'gmail'],
    Calendar: ['calendar', 'calendar'],
    Contacts: ['contacts', 'contacts'],
    Drive: ['drive', 'drive'],
    GitHub: ['github', 'github'],
    LinkedIn: ['linkedin', 'linkedin'],
    'LinkedIn Ads': ['linkedin-ads', 'linkedin'],
    Docs: ['docs', 'docs'],
    Sheets: ['sheets', 'sheets'],
    Slides: ['slides', 'slides'],
    Spotify: ['spotify', 'spotify'],
    'Apple Music': ['applemusic', 'applemusic'],
    Adobe: ['adobe', 'adobe'],
    'Hugging Face': ['huggingface', 'huggingface'],
    Meetup: ['meetup', 'meetup'],
    'Booking.com': ['booking', 'booking'],
    Render: ['render', 'render'],
    'Revolut X': ['revolut', 'revolut'],
  };

  document.querySelectorAll('.integration-logo').forEach((card) => {
    const label = [...card.querySelectorAll('span')]
      .map((element) => element.textContent.trim())
      .find((text) => logoConfig[text]);
    if (!label) return;

    const [symbol, className] = logoConfig[label];
    const existing = card.querySelector('img, .integration-mark, .brand-logo-svg');
    const logo = createBrandLogo(symbol, label, className);
    if (existing) existing.replaceWith(logo);
    else card.prepend(logo);
  });
};

localizeBrandMarks();

const installerLinks = [...document.querySelectorAll('[data-latest-installer]')];
const versionLabels = [...document.querySelectorAll('[data-latest-version]')];

if (installerLinks.length || versionLabels.length) {
  fetch('https://api.github.com/repos/oloix888/Personal-AI-Workspace/releases/latest', {
    headers: {Accept: 'application/vnd.github+json'},
  })
    .then((response) => {
      if (!response.ok) throw new Error(`GitHub release lookup failed: ${response.status}`);
      return response.json();
    })
    .then((release) => {
      const installer = release.assets?.find((asset) =>
        /^Personal-AI-Workspace-Creator-v.*\.md$/i.test(asset.name)
      );
      const target = installer?.browser_download_url || release.html_url;

      installerLinks.forEach((link) => {
        link.href = target;
      });
      versionLabels.forEach((label) => {
        label.textContent = release.tag_name || 'latest';
      });
    })
    .catch(() => {
      // Static links already point to the latest release page and remain usable.
    });
}
