/**
 * Fix My City - Frontend Database Engine (LocalStorage-backed)
 */
const DB_STORAGE_KEY = 'fix_my_city_issues_db_v2';

const INITIAL_SEED_ISSUES = [
    {
        id: 'issue-101',
        title: 'Dangerous Deep Pothole on Oak Avenue',
        description: 'Large, deep pothole near the bike lane causing severe tire damage and risk to cyclists.',
        category: 'Pothole',
        severity: 'High',
        lat: 40.7128,
        lng: -74.0060,
        address: '240 Oak Avenue, Downtown',
        photo: 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=600&q=80',
        upvotes: 14,
        status: 'Council Notified', // >10 upvotes threshold reached
        reporter: 'Citizen #402',
        createdAt: new Date(Date.now() - 3 * 86400000).toISOString(), // 3 days ago
        thresholdNotified: true
    },
    {
        id: 'issue-102',
        title: 'Malfunctioning Pedestrian Light on 5th & Main',
        description: 'Walk signal stays red continuously during peak hours, forcing pedestrians to cross dangerously.',
        category: 'Streetlight',
        severity: 'Critical',
        lat: 40.7150,
        lng: -74.0010,
        address: 'Corner of 5th Ave and Main St',
        photo: 'https://images.unsplash.com/photo-1508873696983-2df515122519?auto=format&fit=crop&w=600&q=80',
        upvotes: 8,
        status: 'Under Review',
        reporter: 'Sarah M.',
        createdAt: new Date(Date.now() - 1 * 86400000).toISOString(), // 1 day ago
        thresholdNotified: false
    },
    {
        id: 'issue-103',
        title: 'Burst Water Pipe & Flooded Sidewalk',
        description: 'Clean water gushing from underground main. Creating icy slick patches and water waste.',
        category: 'Water Leak',
        severity: 'High',
        lat: 40.7090,
        lng: -74.0120,
        address: '88 River Street',
        photo: 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=600&q=80',
        upvotes: 21,
        status: 'Scheduled for Repair',
        reporter: 'Alex K.',
        createdAt: new Date(Date.now() - 5 * 86400000).toISOString(),
        thresholdNotified: true
    },
    {
        id: 'issue-104',
        title: 'Illegal Trash Dumping behind Community Center',
        description: 'Piles of discarded furniture and construction debris blocking fire egress route.',
        category: 'Sanitation',
        severity: 'Medium',
        lat: 40.7180,
        lng: -74.0080,
        address: '12 Community Lane',
        photo: 'https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=600&q=80',
        upvotes: 4,
        status: 'Pending Verification',
        reporter: 'EcoWatch Group',
        createdAt: new Date(Date.now() - 12 * 3600000).toISOString(), // 12 hours ago
        thresholdNotified: false
    },
    {
        id: 'issue-105',
        title: 'Graffiti Vandalism on Historic Fountain',
        description: 'Spray paint tagging on the marble base of the public park fountain.',
        category: 'Graffiti',
        severity: 'Low',
        lat: 40.7110,
        lng: -73.9980,
        address: 'Washington Square Park',
        photo: 'https://images.unsplash.com/photo-1525909002-1b05e0c869d8?auto=format&fit=crop&w=600&q=80',
        upvotes: 11,
        status: 'Council Notified',
        reporter: 'Historic Guild',
        createdAt: new Date(Date.now() - 4 * 86400000).toISOString(),
        thresholdNotified: true
    }
];

class CivicDB {
    constructor() {
        this.init();
    }

    init() {
        const existingData = localStorage.getItem(DB_STORAGE_KEY);
        if (!existingData) {
            this.saveAll(INITIAL_SEED_ISSUES);
        }
    }

    getAll() {
        try {
            const data = localStorage.getItem(DB_STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Failed to read from local storage:', e);
            return INITIAL_SEED_ISSUES;
        }
    }

    saveAll(issues) {
        try {
            localStorage.setItem(DB_STORAGE_KEY, JSON.stringify(issues));
        } catch (e) {
            console.error('Failed to save to local storage:', e);
        }
    }

    getById(id) {
        return this.getAll().find(issue => issue.id === id) || null;
    }

    addIssue(newIssueData) {
        const issues = this.getAll();
        const newIssue = {
            id: 'issue-' + Date.now(),
            title: newIssueData.title || 'Untitled Civic Issue',
            description: newIssueData.description || 'No description provided.',
            category: newIssueData.category || 'Other',
            severity: newIssueData.severity || 'Medium',
            lat: parseFloat(newIssueData.lat),
            lng: parseFloat(newIssueData.lng),
            address: newIssueData.address || `${newIssueData.lat.toFixed(4)}, ${newIssueData.lng.toFixed(4)}`,
            photo: newIssueData.photo || null,
            upvotes: 1, // Start with reporter's upvote
            status: 'Pending Verification',
            reporter: newIssueData.reporter || 'Anonymous Citizen',
            createdAt: new Date().toISOString(),
            thresholdNotified: false
        };

        issues.unshift(newIssue); // Place newest first
        this.saveAll(issues);
        return newIssue;
    }

    upvoteIssue(id) {
        const issues = this.getAll();
        const issue = issues.find(i => i.id === id);
        if (!issue) return null;

        issue.upvotes += 1;

        // Proposal feature: Automatic notification threshold when upvotes reach 10
        if (issue.upvotes >= 10 && !issue.thresholdNotified && issue.status === 'Pending Verification') {
            issue.status = 'Council Notified';
            issue.thresholdNotified = true;
        }

        this.saveAll(issues);
        return issue;
    }

    filter({ category = 'all', search = '', status = 'all', sortBy = 'upvotes' } = {}) {
        let issues = this.getAll();

        if (category && category !== 'all') {
            issues = issues.filter(i => i.category.toLowerCase() === category.toLowerCase());
        }

        if (status && status !== 'all') {
            issues = issues.filter(i => i.status.toLowerCase().includes(status.toLowerCase()));
        }

        if (search && search.trim() !== '') {
            const query = search.toLowerCase();
            issues = issues.filter(i => 
                i.title.toLowerCase().includes(query) || 
                i.description.toLowerCase().includes(query) ||
                i.address.toLowerCase().includes(query) ||
                i.category.toLowerCase().includes(query)
            );
        }

        // Sorting
        if (sortBy === 'upvotes') {
            issues.sort((a, b) => b.upvotes - a.upvotes);
        } else if (sortBy === 'newest') {
            issues.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        } else if (sortBy === 'oldest') {
            issues.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
        }

        return issues;
    }

    getStats() {
        const issues = this.getAll();
        return {
            total: issues.length,
            pending: issues.filter(i => i.status === 'Pending Verification' || i.status === 'Under Review').length,
            notified: issues.filter(i => i.status === 'Council Notified').length,
            resolved: issues.filter(i => i.status === 'Scheduled for Repair' || i.status === 'Resolved').length
        };
    }
}

// Global instance
window.civicDB = new CivicDB();
