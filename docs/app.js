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

const installerLinks = [...document.querySelectorAll('[data-latest-installer]')];
const versionLabels = [...document.querySelectorAll('[data-latest-version]')];

if (installerLinks.length || versionLabels.length) {
  fetch('https://api.github.com/repos/oloix888/Personal-AI-Workspace/releases/latest', {
    headers: { Accept: 'application/vnd.github+json' }
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
      // The static links already point to the latest release page and remain usable.
    });
}
