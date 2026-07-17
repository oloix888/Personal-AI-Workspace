const menuButton = document.querySelector('.nav-toggle');
const navigation = document.querySelector('.site-header nav');

menuButton?.addEventListener('click', () => {
  const open = navigation.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(open));
});

navigation?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navigation.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
  });
});

const localizeBrandMarks = () => {
  const openAiPanel = document.querySelector('.platform-logo-pair');
  if (openAiPanel) {
    openAiPanel.classList.add('required-artwork');
    openAiPanel.innerHTML = '<img src="assets/required-chatgpt-codex.svg" alt="ChatGPT or Codex">';
  }

  const notionPanel = document.querySelector('.platform-logo-single');
  if (notionPanel) {
    notionPanel.classList.add('required-artwork');
    notionPanel.innerHTML = '<img src="assets/required-notion.svg" alt="Notion">';
  }

  const markConfig = {
    'Gmail': ['gmail', 'M'],
    'Calendar': ['calendar', '31'],
    'Contacts': ['contacts', 'C'],
    'Drive': ['drive', 'D'],
    'GitHub': ['github', 'GH'],
    'LinkedIn': ['linkedin', 'in'],
    'LinkedIn Ads': ['linkedin-ads', 'in'],
    'Docs': ['docs', 'D'],
    'Sheets': ['sheets', 'S'],
    'Slides': ['slides', 'S'],
    'Spotify': ['spotify', '♫'],
    'Apple Music': ['apple', '♪'],
    'Adobe': ['adobe', 'A'],
    'Hugging Face': ['huggingface', 'HF'],
    'Meetup': ['meetup', 'M'],
    'Booking.com': ['booking', 'B'],
    'Render': ['render', 'R'],
    'Revolut X': ['revolut', 'RX'],
  };

  document.querySelectorAll('.integration-logo').forEach((card) => {
    const label = [...card.querySelectorAll('span')]
      .map((element) => element.textContent.trim())
      .find((text) => markConfig[text]);
    const image = card.querySelector('img');
    if (!label || !image) return;

    const [className, abbreviation] = markConfig[label];
    const mark = document.createElement('span');
    mark.className = `integration-mark ${className}`;
    mark.textContent = abbreviation;
    mark.setAttribute('aria-hidden', 'true');
    image.replaceWith(mark);
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
