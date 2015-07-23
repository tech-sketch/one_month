$(document).ready(function() {
				$('#pagepiling').pagepiling({
					direction : 'horizontal',
					menu : '#menu',
					anchors : ['page1', 'page2', 'page3', 'page4'],
					navigation : {
						'position' : 'right',
						'tooltips' : ['section1', 'section2', 'section3', 'section4']
					},
					scrollingSpeed : 1000,
					sectionSelector : '.contents'
				});
			});