import bandit
d = bandit.get_distribution(__package__)
metadata = d._get_metadata(d.PKG_INFO)
home_page = [m for m in metadata if m.startswith('Home-page:')]
url = home_page[0].split(':', 1)[1].strip()