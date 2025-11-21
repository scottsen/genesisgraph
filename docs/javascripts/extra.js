// GenesisGraph Documentation - Extra JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Add copy button functionality enhancements
  const codeBlocks = document.querySelectorAll('pre code');

  codeBlocks.forEach(function(codeBlock) {
    // Add language label if detected
    const language = codeBlock.className.match(/language-(\w+)/);
    if (language && language[1]) {
      const label = document.createElement('div');
      label.className = 'code-label';
      label.textContent = language[1].toUpperCase();
      label.style.cssText = 'position: absolute; top: 0; right: 45px; padding: 4px 8px; font-size: 0.7em; background: rgba(0,0,0,0.2); border-radius: 0 0 4px 4px; color: #fff;';
      codeBlock.parentElement.style.position = 'relative';
      codeBlock.parentElement.insertBefore(label, codeBlock);
    }
  });

  // Add anchor link highlighting on scroll
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.intersectionRatio > 0) {
        const id = entry.target.getAttribute('id');
        const tocLink = document.querySelector(`.md-nav__link[href="#${id}"]`);
        if (tocLink) {
          // Remove all active states
          document.querySelectorAll('.md-nav__link--active').forEach(link => {
            link.classList.remove('md-nav__link--active');
          });
          // Add active state to current
          tocLink.classList.add('md-nav__link--active');
        }
      }
    });
  }, {
    rootMargin: '-20% 0px -35% 0px'
  });

  // Observe all headings
  document.querySelectorAll('h2[id], h3[id], h4[id]').forEach(heading => {
    observer.observe(heading);
  });

  // Add version indicator
  const version = '0.3.0';
  const header = document.querySelector('.md-header__title');
  if (header) {
    const versionBadge = document.createElement('span');
    versionBadge.textContent = `v${version}`;
    versionBadge.style.cssText = 'font-size: 0.7em; margin-left: 8px; padding: 2px 6px; background: rgba(255,255,255,0.2); border-radius: 3px;';
    header.appendChild(versionBadge);
  }

  // Enhanced search functionality
  const searchInput = document.querySelector('.md-search__input');
  if (searchInput) {
    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.toLowerCase();

      // Highlight search terms in results
      setTimeout(() => {
        const results = document.querySelectorAll('.md-search-result__article');
        results.forEach(result => {
          const text = result.textContent;
          if (query && text.toLowerCase().includes(query)) {
            result.style.backgroundColor = 'rgba(74, 144, 226, 0.05)';
          } else {
            result.style.backgroundColor = '';
          }
        });
      }, 100);
    });
  }

  // Add "Edit on GitHub" link to each page
  const content = document.querySelector('.md-content');
  if (content) {
    const editLink = document.createElement('a');
    const currentPath = window.location.pathname.replace('/genesisgraph/', '');
    editLink.href = `https://github.com/scottsen/genesisgraph/edit/main/docs${currentPath}`;
    editLink.textContent = '✏️ Edit this page';
    editLink.className = 'md-button md-button--primary';
    editLink.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 100; font-size: 0.8em;';
    editLink.target = '_blank';
    document.body.appendChild(editLink);
  }

  // Add keyboard shortcuts hint
  document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchButton = document.querySelector('.md-search__icon');
      if (searchButton) {
        searchButton.click();
      }
    }
  });

  // Add scroll-to-top button
  const scrollButton = document.createElement('button');
  scrollButton.innerHTML = '↑';
  scrollButton.className = 'scroll-to-top';
  scrollButton.style.cssText = 'position: fixed; bottom: 80px; right: 20px; width: 40px; height: 40px; border-radius: 50%; background: #4a90e2; color: white; border: none; cursor: pointer; display: none; z-index: 99; font-size: 1.5em; box-shadow: 0 2px 8px rgba(0,0,0,0.2);';
  document.body.appendChild(scrollButton);

  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      scrollButton.style.display = 'block';
    } else {
      scrollButton.style.display = 'none';
    }
  });

  scrollButton.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // Console message for developers
  console.log('%cGenesisGraph Documentation', 'font-size: 20px; font-weight: bold; color: #4a90e2;');
  console.log('%cVersion: 0.3.0', 'font-size: 12px; color: #666;');
  console.log('%cContribute: https://github.com/scottsen/genesisgraph', 'font-size: 12px; color: #666;');
});
