
        function toggleMenu() {
            const nav = document.getElementById('menu');
            nav.classList.toggle('active');
        }

        function toggleAccordion(event) {
            const content = event.currentTarget.nextElementSibling;
            content.classList.toggle('active');
        }

        function updateProgress() {
            const checkboxes = document.querySelectorAll('.goal-checkbox');
            const total = checkboxes.length;
            const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
            const remaining = total - checked;
            const percent = Math.round((checked / total) * 100);
            
            document.getElementById('completedCount').textContent = checked;
            document.getElementById('totalCount').textContent = total;
            document.getElementById('remainingCount').textContent = remaining;
            document.getElementById('progressPercentage').textContent = percent + '%';
            
            const progressBar = document.getElementById('progressBarFill');
            progressBar.style.width = percent + '%';
            
            const milestone = document.getElementById('milestoneMessage');
            if (percent === 100) {
                milestone.style.display = 'block';
                milestone.textContent = "🎉 Congratulations! You've completed all your tasks! 🎉";
            } else if (percent === 50) {
                milestone.style.display = 'block';
                milestone.textContent = "🔥 Halfway there! Keep up the great work! ";
            } else {
                milestone.style.display = 'none';
            }
        }

        document.querySelectorAll('.goal-checkbox').forEach(cb => {
            cb.addEventListener('change', updateProgress);
        });
        
        window.onload = updateProgress;
