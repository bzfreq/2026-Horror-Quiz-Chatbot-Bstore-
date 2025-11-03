// ===== HORROR ORACLE JAVASCRIPT =====
// This file connects the HTML frontend to the Python Flask backend

// Global variables
let currentMovie = null;
let currentMovieDetails = null; // NEW - Store full movie object for persistent buttons
let currentMovieStats = null;
let lastDisplayedMovie = null;
let userRating = 0;
let isLoading = false;

// Session management
let sessionId = null;
let userGoogleId = null;
let horrorSession = null; // Persistent session for oracle_converse

// Initialize session ID on load
function initSession() {
    // Try to get existing session from storage
    sessionId = sessionStorage.getItem('oracle_session_id');
    
    if (!sessionId) {
        // Generate new UUID for session
        sessionId = 'web_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('oracle_session_id', sessionId);
        console.log('🔑 New session started:', sessionId);
    } else {
        console.log('🔑 Resuming session:', sessionId);
    }
    
    // Initialize persistent horror session for oracle_converse
    horrorSession = localStorage.getItem("horror_session_id");
    if (!horrorSession) {
        horrorSession = crypto.randomUUID();
        localStorage.setItem("horror_session_id", horrorSession);
        console.log('🩸 New horror session:', horrorSession);
    } else {
        console.log('🩸 Resuming horror session:', horrorSession);
    }
    
    // Get Google ID if available (from sign-in)
    try {
        // Try to get from window.user first (legacy)
        const user = window.user;
        if (user && user.sub) {
            userGoogleId = user.sub;
        } else {
            // Fallback to localStorage (current implementation)
            const savedUser = localStorage.getItem('horrorUser');
            if (savedUser) {
                const userObject = JSON.parse(savedUser);
                if (userObject && userObject.sub) {
                    userGoogleId = userObject.sub;
                }
            }
        }
    } catch (e) {
        // User not signed in
    }
}

// Initialize session when page loads
initSession();

// API Base URL - adjust if needed
const API_BASE = 'http://localhost:5000';

// ===== PREFETCH SYSTEM FOR CONTINUOUS QUIZ FLOW =====
let nextQuizCache = null;
let prefetchInProgress = false;

// NOTE: Background music/sounds continuity is preserved by not tearing down DOM
// Audio elements persist through transitions, keeping ambient sounds running

// ===== DOM ELEMENTS =====
const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const myListContainer = document.getElementById('my-list-container');
const recommendationsContainer = document.getElementById('recommendations-container');
const streamingContainer = document.getElementById('streaming-container');
const videoModal = document.getElementById('video-modal');
const videoIframe = document.getElementById('video-iframe');
const videoClose = document.querySelector('.video-close');

// ===== DYNAMIC BLOOD SHOP DATA GENERATOR =====
function generateBloodShopItems(movieTitle) {
    // Generate 15 dynamic items based on ANY movie title
    const dynamicItems = [
        {
            title: `${movieTitle} DVD Collection`,
            price: "$29.99",
            image: "https://m.media-amazon.com/images/I/81kQYvR3xCdL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+dvd`
        },
        {
            title: `${movieTitle} Blu-Ray 4K`,
            price: "$39.99",
            image: "https://m.media-amazon.com/images/I/91mFQZ2WNYL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+blu+ray+4k`
        },
        {
            title: `${movieTitle} Movie Poster`,
            price: "$24.99",
            image: "https://m.media-amazon.com/images/I/81ZSsUdkr7L._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+movie+poster`
        },
        {
            title: `${movieTitle} T-Shirt`,
            price: "$19.99",
            image: "https://m.media-amazon.com/images/I/81A9YgJAP8L._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+t+shirt`
        },
        {
            title: `${movieTitle} Action Figure`,
            price: "$34.99",
            image: "https://m.media-amazon.com/images/I/81gPmGYqo9L._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+action+figure`
        },
        {
            title: `${movieTitle} Mask Replica`,
            price: "$89.99",
            image: "https://m.media-amazon.com/images/I/81OzKxH1BYL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+mask+replica`
        },
        {
            title: `${movieTitle} Soundtrack Vinyl`,
            price: "$39.99",
            image: "https://m.media-amazon.com/images/I/81MPKKszMmL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+soundtrack+vinyl`
        },
        {
            title: `${movieTitle} VHS Collector's Edition`,
            price: "$149.99",
            image: "https://m.media-amazon.com/images/I/91mFQZ2WNYL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+vhs`
        },
        {
            title: `${movieTitle} Coffee Mug`,
            price: "$14.99",
            image: "https://m.media-amazon.com/images/I/71x5Qa-DXNL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+coffee+mug`
        },
        {
            title: `${movieTitle} Prop Replica`,
            price: "$69.99",
            image: "https://m.media-amazon.com/images/I/71ZgxBgRdjL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+prop+replica`
        },
        {
            title: `${movieTitle} Board Game`,
            price: "$59.99",
            image: "https://m.media-amazon.com/images/I/81jB3xKuUWL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+board+game`
        },
        {
            title: `${movieTitle} Hoodie`,
            price: "$49.99",
            image: "https://m.media-amazon.com/images/I/81A9YgJAP8L._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+hoodie`
        },
        {
            title: `${movieTitle} Pin Badge Set`,
            price: "$12.99",
            image: "https://m.media-amazon.com/images/I/61ggPCF6vYL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+pin+badge`
        },
        {
            title: `${movieTitle} Art Print`,
            price: "$34.99",
            image: "https://m.media-amazon.com/images/I/81ZSsUdkr7L._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+art+print`
        },
        {
            title: `${movieTitle} Collector's Box Set`,
            price: "$199.99",
            image: "https://m.media-amazon.com/images/I/81kQYvR3xCdL._AC_UL320_.jpg",
            buyLink: `https://www.amazon.com/s?k=${encodeURIComponent(movieTitle)}+collector+box+set`
        }
    ];
    
    return dynamicItems;
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🩸 Horror Oracle Frontend Loading...');
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    loadTheaterReleases();
    loadDailyObscureGems();
    loadMyList();
    
    // Start blood effects
    startBloodEffects();
    
    console.log('✅ Horror Oracle Frontend Ready!');
});

/**
 * Preload slideshow images in background for instant slideshow start
 */
function preloadSlideshowImages() {
    const horrorImages = [
        'butcher.png',
        'zombsing.png',
        'zombie girl screaming.png',
        'terrifiedwomen.png',
        'preecher.png',
        'jasonlike.png'
    ];
    
    console.log('🖼️ Preloading slideshow images...');
    horrorImages.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

/**
 * Horror Flash Effect - Random sudden image flashes
 */
function initHorrorFlash() {
    const horrorImages = [
        "/static/images/horror_flash/priest.jpg",
        "/static/images/horror_flash/butcher.jpg",
        "/static/images/horror_flash/zombie.jpg",
        "/static/images/horror_flash/possessed_woman.jpg",
        "/static/images/horror_flash/shadow_face.jpg"
    ];

    const flash = document.getElementById("horror-flash");
    
    if (!flash) {
        console.warn('⚠️ Horror flash element not found');
        return;
    }

    function showHorrorFlash() {
        const randomImage = horrorImages[Math.floor(Math.random() * horrorImages.length)];
        flash.style.backgroundImage = `url(${randomImage})`;
        flash.style.opacity = 1;
        setTimeout(() => (flash.style.opacity = 0), 2000); // visible for 2 seconds
    }

    // Start the flash system after 10 seconds, then repeat every 60 seconds
    setTimeout(() => {
        setInterval(() => {
            // random delay 30–60 seconds between flashes
            const randomDelay = Math.random() * 30000 + 30000;
            setTimeout(showHorrorFlash, randomDelay);
        }, 60000);
    }, 10000); // start 10 seconds after load
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Chat input handling
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    sendBtn.addEventListener('click', sendMessage);
    
    // Video modal handling
    videoClose.addEventListener('click', closeVideoModal);
    videoModal.addEventListener('click', function(e) {
        if (e.target === videoModal) {
            closeVideoModal();
        }
    });
    
    // Rating system
    setupRatingSystem();
    
	// Info button
	const infoBtn = document.querySelector('.info-btn');
	if (infoBtn) infoBtn.addEventListener('click', showAboutModal);
	setupGenreButtons();
}

// ===== CHAT FUNCTIONALITY =====
async function sendMessage() {
    const query = userInput.value.trim();
    if (!query || isLoading) return;
    
    isLoading = true;
    
    // Hide the initial horror image when user searches
    const initialImage = document.getElementById('initial-horror-image');
    if (initialImage) {
        initialImage.style.display = 'none';
    }
    
    // Add user message to chat
    addChatMessage('user', query);
    userInput.value = '';
    
    // Show loading indicator
    const loadingId = addChatMessage('bot', 'The Oracle is searching the depths of horror cinema...', null, true);
    
    try {
        // Use RLOM Cognitive endpoint for full memory continuity
        const response = await fetch(`${API_BASE}/api/rlom`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                user_id: userGoogleId || 'anon',
                message: query,
                history: localStorage.getItem("chat_history") || "",
                text: query,  // Keep for backward compatibility
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        // Remove loading message
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();
        
        if (data.error) {
            addChatMessage('bot', `Error: ${data.error}`);
        } else {
            // Use answer field from response, fallback to response for backward compatibility
            const responseText = data.answer || data.response;
            
            // Store context if provided
            if (data.context) {
                localStorage.setItem("chat_context", JSON.stringify(data.context));
            }
            
// Add Oracle's response - prevent duplicates
  const isDuplicate = data.movie_details && 
                   data.movie_details.title &&
                   lastDisplayedMovie === data.movie_details.title;

if (!isDuplicate) {
    addChatMessage('bot', responseText, data.movie_details);
    lastDisplayedMovie = data.movie_details ? data.movie_details.title : null;
}
 
            
            // Update movie-specific sections
            if (data.movie_details && data.movie_details.title) {
                currentMovie = data.movie_details.title;
                currentMovieDetails = data.movie_details; // NEW - Save full movie details
                updateMovieSections(data.movie_details, data.recommendations);
                loadMovieStats(currentMovie);
            } else if (data.recommendations && data.recommendations.length > 0) {
                updateRecommendations(data.recommendations);
            }
            
            // Handle personality transition message
            if (data.personality_transition) {
                // Small delay for dramatic effect
                setTimeout(() => {
                    addChatMessage('bot', data.personality_transition);
                }, 800);
            }
            
            // Log conversation metadata for debugging
            if (data.conversation_turn || data.personality_tone) {
                console.log('🗣️  Conversation turn:', data.conversation_turn, '| Personality:', data.personality_tone);
            }
            
            // Log RLOM metadata if present
            if (data._rlom_metadata) {
                console.log('🧠 RLOM:', data._rlom_metadata);
            }
        }
    } catch (error) {
        console.error('Chat error:', error);
        
        // Remove loading message
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();
        
        addChatMessage('bot', 'The spirits are restless... Please try again.');
    }
    
    isLoading = false;
}

// Oracle conversational chat with persistent session
async function sendHorrorMessage(userText) {
  const payload = {
    message: userText,
    session_id: horrorSession
  };
  
  const res = await fetch("/oracle_converse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  
  const data = await res.json();
  addChatMessage('bot', data.reply || "The Oracle whispers... but is unclear.");
}

function addChatMessage(type, message, movieDetails = null, isLoading = false) {
    const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-bubble ${type}-bubble`;
    messageDiv.id = messageId;
    
    let content = '';
    
    if (type === 'bot') {
        if (isLoading) {
            content = `
                <div class="flex items-center space-x-2">
                    <div class="skeleton-loading w-4 h-4 rounded-full"></div>
                    <span>${message}</span>
                </div>
            `;
        } else {
            content = `<p class="mb-2">${message}</p>`;
            
            // NEW - Use passed movieDetails OR stored currentMovieDetails
            const movieToDisplay = movieDetails || currentMovieDetails;
            
            // Add movie poster if available
            if (movieToDisplay && movieToDisplay.poster) {
                content += `
                    <div class="flex items-start space-x-3 mt-3">
                        <img src="${movieToDisplay.poster}" 
                             alt="${movieToDisplay.title}" 
                             class="movie-poster-inline w-24 h-36 object-cover rounded-lg border-2 border-red-600"
                             onerror="this.src='https://via.placeholder.com/100x150/000000/FF0000?text=No+Poster'">
                        <div class="flex-1">
                            <h3 class="text-white font-bold">${movieToDisplay.title}</h3>
                            ${movieToDisplay.year ? `<p class="text-gray-400 text-sm">${movieToDisplay.year}</p>` : ''}
                            ${movieToDisplay.director ? `<p class="text-gray-400 text-sm">Dir: ${movieToDisplay.director}</p>` : ''}
                            ${movieToDisplay.rating ? `<p class="text-yellow-400 text-sm">⭐ ${movieToDisplay.rating}</p>` : ''}
                            ${movieToDisplay.plot ? `<p class="text-gray-300 text-sm mt-2 line-clamp-3">${movieToDisplay.plot}</p>` : ''}
                        </div>
                    </div>
                `;
                
              }
                
                // Add action buttons - NOW WITH 5TH BUTTON
                if (movieToDisplay && movieToDisplay.title) {
                content += `

                    <div class="flex space-x-2 mt-3">
                        <button onclick="watchTrailer('${movieToDisplay.title}')" 
                                class="px-3 py-1 bg-red-600 text-white text-sm rounded-full hover:bg-red-700 transition-colors">
                            🎬 Watch Trailer
                        </button>
                        <button onclick="tellMeMore('${movieToDisplay.title}')" 
                                class="px-3 py-1 bg-gray-600 text-white text-sm rounded-full hover:bg-gray-700 transition-colors">
                            📖 Tell Me More
                        </button>
                        <button onclick="addToMyList('${movieToDisplay.title}')" 
                                class="px-3 py-1 bg-green-600 text-white text-sm rounded-full hover:bg-green-700 transition-colors">
                            ➕ Add to List
                        </button>
                        <button onclick="suggestSimilar('${movieToDisplay.title}')" 
                                class="px-3 py-1 bg-purple-600 text-white text-sm rounded-full hover:bg-purple-700 transition-colors">
                            ✨ Movies Like This
                        </button>
                        <button onclick="openBloodShop('${movieToDisplay.title}')" 
                                class="px-3 py-1 bg-red-600 text-white text-sm rounded-full hover:bg-red-700 transition-colors">
                            🩸 Blood Shop
                        </button>
<button onclick="openBloodQuiz('${movieToDisplay.title}')" 
        class="px-3 py-1 bg-blue-900 text-white text-sm rounded-full hover:bg-blue-700 transition-colors">
    🩸 Blood Quiz
</button>

                    </div>
                `;
            }
        }
    } else {
        content = `<p>${message}</p>`;
    }
    
    messageDiv.innerHTML = content;
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    return messageId;
}

// ===== MOVIE-SPECIFIC ACTIONS =====
async function tellMeMore(movieTitle) {
    if (isLoading) return;
      
    const query = `Tell me more obscure details about ${movieTitle}`;
    userInput.value = query;
    await sendMessage();
}
// NEW FUNCTION - Suggest Similar Movies (FIXED)
async function suggestSimilar(movieTitle) {
    if (isLoading) return;
    
    // Get all recommendation cards
    const recContainer = document.getElementById('recommendations-container');
    const allRecs = recContainer.querySelectorAll('.rec-card');
    
    if (allRecs.length > 0) {
        // Get titles from recommendations
        for (let i = 0; i < allRecs.length; i++) {
            const recTitle = allRecs[i].querySelector('h4').textContent;
            
            // Skip if it's the same movie - get the NEXT one
            if (recTitle.toLowerCase() !== movieTitle.toLowerCase()) {
                // Found a DIFFERENT movie! Search for it
                userInput.value = recTitle;
                await sendMessage();
                return;
            }
        }
    }
    
    // Fallback: trigger a search query to get recommendations
    const query = `Show me movies similar to ${movieTitle}`;
    userInput.value = query;
    await sendMessage();
}

async function watchTrailer(movieTitle) {
    try {
        const response = await fetch(`${API_BASE}/get-trailer?title=${encodeURIComponent(movieTitle)}`);
        const data = await response.json();
        
        if (data.trailer_url) {
            showTrailer(data.trailer_url);
        } else {
            alert('Trailer not found for this movie.');
        }
    } catch (error) {
        console.error('Error loading trailer:', error);
        alert('Could not load trailer. Please try again.');
    }
}

// ===== BLOOD SHOP FUNCTIONALITY =====
function openBloodShop(movieTitle) {
    // Generate dynamic items based on movie
    const bloodShopItems = generateBloodShopItems(movieTitle);
    
    // Create modal backdrop
    const modal = document.createElement('div');
    modal.id = 'bloodShopModal';
    modal.className = 'fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50';
    modal.style.backdropFilter = 'blur(5px)';
    
    // Create modal content with horror theme
    modal.innerHTML = `
        <div class="bg-gradient-to-b from-gray-900 via-red-900 to-black border-4 border-red-800 rounded-lg max-w-6xl w-11/12 max-h-5/6 overflow-hidden shadow-2xl relative">
            <!-- Close button -->
            <button onclick="closeBloodShop()" 
                    class="absolute top-4 right-4 text-red-400 hover:text-red-200 text-3xl font-bold z-10 transition-colors">
                ✕
            </button>
            
            <!-- Header -->
            <div class="bg-gradient-to-r from-red-800 to-black p-6 border-b-4 border-red-700">
                <h2 class="text-3xl font-bold text-red-400 text-center" style="text-shadow: 0 0 20px rgba(255, 0, 0, 0.8);">
                    🩸 BLOOD SHOP 🩸
                </h2>
                <p class="text-gray-300 text-center mt-2">Horror Collectibles Inspired by "${movieTitle}"</p>
            </div>
            
            <!-- Products Grid -->
            <div class="p-6 overflow-y-auto max-h-96" style="background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><rect width=\"100\" height=\"100\" fill=\"%23111\"/><path d=\"M10,10 L90,10 L90,90 L10,90 Z\" fill=\"none\" stroke=\"%23333\" stroke-width=\"2\"/><circle cx=\"20\" cy=\"20\" r=\"2\" fill=\"%23444\"/><circle cx=\"80\" cy=\"80\" r=\"2\" fill=\"%23444\"/></svg>');">
                <div class="grid grid-cols-3 md:grid-cols-5 gap-4">
                    ${bloodShopItems.map(item => `
                        <div class="bg-black bg-opacity-60 border-2 border-red-700 rounded-lg p-3 hover:border-red-500 transition-all duration-300 hover:shadow-lg hover:shadow-red-900/50">
                            <img src="${item.image}" 
                                 alt="${item.title}" 
                                 class="w-full h-32 object-cover rounded border border-red-600 mb-2"
                                 onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjIyIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iI2ZmMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkhPUlJPUjwvdGV4dD48L3N2Zz4='">
                            
                            <h3 class="text-red-300 font-bold text-xs mb-1 line-clamp-2">${item.title}</h3>
                            <p class="text-red-400 font-bold text-sm mb-2">${item.price}</p>
                            
                            <a href="${item.buyLink}" 
                               target="_blank" 
                               class="block w-full bg-red-700 hover:bg-red-600 text-white text-xs font-bold py-1 px-2 rounded text-center transition-colors">
                                BUY NOW
                            </a>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- Footer -->
            <div class="bg-gradient-to-r from-black to-red-900 p-4 border-t-4 border-red-700 text-center">
                <p class="text-gray-400 text-sm">
                    ⚠️ WARNING: Items may contain traces of supernatural energy ⚠️
                </p>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeBloodShop();
        }
    });
}

function closeBloodShop() {
    const modal = document.getElementById('bloodShopModal');
    if (modal) {
        modal.remove();
    }
}

// ===== BLOOD QUIZ FUNCTIONALITY - AI-ADAPTIVE =====
// ===== LANGCHAIN QUIZ INTEGRATION - COMPLETE DATA FLOW =====
//
// QUIZ INITIALIZATION FLOW:
//   1. User clicks "Face Your Nightmares" or "Start Trial" → startOracleQuiz() or openBloodQuiz()
//   2. Frontend calls unified startQuiz() → POST /api/start_quiz
//   3. Backend (Flask) → Oracle Engine (LangChain):
//      - Builder Node generates questions based on user profile
//      - Profile Node loads/creates player profile
//      - Lore Whisperer Node generates atmospheric intro
//      - Fear Meter Node initializes fear state
//   4. Backend returns JSON: { room, intro, questions[], theme, difficulty, lore, oracle_state, player_profile }
//   5. Frontend normalizes and renders quiz using displayQuizWithData() or displayOracleQuiz()
//
// QUIZ SUBMISSION FLOW:
//   1. User answers all questions → checkAnswer() tracks answers in currentQuiz.answers[]
//   2. After last question → submitToOracle() → unified submitAnswers()
//   3. Frontend calls POST /api/submit_answers with { user_id, quiz, answers }
//   4. Backend (Flask) → Oracle Engine (LangChain):
//      - Evaluator Node scores answers and generates Oracle reaction
//      - Fear Meter Node updates emotional state based on performance
//      - Reward Node generates rewards based on score
//      - Profile Node updates player stats (bravery, fear_level, etc.)
//      - Recommender Node generates personalized movie recommendations
//      - Lore Whisperer Node generates transition lore
//   5. Backend returns: { score, out_of, percentage, evaluation: { oracle_reaction }, 
//                         rewards: { reward_name, reward_description }, 
//                         recommendations: [{ title, year, poster, reason }],
//                         next_difficulty, next_theme, player_profile, lore }
//   6. Frontend displays results via displayOracleResults() showing:
//      - Score and percentage
//      - Oracle's reaction (from LangChain Evaluator)
//      - Rewards (from LangChain Reward Node)
//      - Movie recommendations (from LangChain Recommender Node)
//      - Updated fear level and player profile
//      - Lore fragment (from LangChain Lore Whisperer)
//
// KEY CHANGES MADE:
//   - All quiz data now comes from LangChain backend (no static arrays)
//   - Unified startQuiz() function replaces all old quiz initialization
//   - Unified submitAnswers() function replaces all old result calculations
//   - Old static functions (getQuizQuestions) marked as DEPRECATED
//   - All entry points (Face Your Nightmares, openBloodQuiz) use unified functions
//
// ===== END DATA FLOW COMMENT =====

let currentQuiz = {
    questions: [],
    currentQuestion: 0,
    score: 0,
    category: 'general',
    quizNumber: 1,
    theme: '',
    difficulty: '',
    answers: [],
    profileAnswers: [],
    oracleData: null  // NEW: Store Oracle Engine quiz data
};

// ===== ORACLE ENGINE STATE =====
let oracleState = {
    fearLevel: 50,
    currentTone: 'neutral',
    userId: 'guest',
    isOracleMode: false,  // Flag to track if using Oracle Engine
    nextDifficulty: null,  // Store next difficulty from evaluation
    nextTheme: null  // Store next theme from evaluation
};

async function openBloodQuiz(movieTitle) {
    // Always generate fresh quiz data (no caching)
    const startTime = Date.now();
    
    // Start preloading quiz in the background
    const quizLoadPromise = preloadQuizData(movieTitle);
    
    // Wait a brief moment to see if quiz loads instantly
    const quickLoadTimeout = new Promise(resolve => setTimeout(resolve, 200));
    await quickLoadTimeout;
    
    const loadTime = Date.now() - startTime;
    let quizData = null;
    
    // Check if quiz loaded in under 300ms (considered "instant")
    try {
        const result = await Promise.race([
            quizLoadPromise,
            new Promise((_, reject) => setTimeout(() => reject('timeout'), 300))
        ]);
        quizData = result;
        const totalLoadTime = Date.now() - startTime;
        
        if (totalLoadTime < 500) {
            // Quiz loaded quickly - SKIP slideshow, go directly to text intro
            showHorrorTextIntro(movieTitle, quizData);
        } else {
            // Quiz needs loading time - show slideshow while loading
            playCinematicIntroWithPreload(movieTitle, quizLoadPromise);
        }
    } catch (error) {
        // Quiz is taking time to load - show slideshow
        playCinematicIntroWithPreload(movieTitle, quizLoadPromise);
    }
}

function playCinematicIntroWithPreload(movieTitle, quizLoadPromise) {
    // Horror images for slideshow (using correct filenames from project)
    const horrorImages = [
        'butcher.png',
        'zombsing.png',
        'zombie girl screaming.png',
        'terrifiedwomen.png',
        'preecher.png',
        'jasonlike.png'
    ];
    
    // Shuffle images for random order
    const shuffledImages = horrorImages.sort(() => Math.random() - 0.5);
    
    // Create intro overlay
    const introOverlay = document.createElement('div');
    introOverlay.id = 'nightmare-intro-overlay';
    
    introOverlay.innerHTML = `
        <div class="intro-bg-slideshow">
            ${shuffledImages.map((img, index) => 
                `<img src="${img}" class="intro-bg-image ${index === 0 ? 'active' : ''}" alt="Horror">`
            ).join('')}
        </div>
        <div class="intro-text-container">
            <div class="intro-line" data-delay="0">Loading your nightmare...</div>
            <div class="intro-line" data-delay="1500">The darkness awaits...</div>
            <div class="intro-line loading-pulse" data-delay="3000" style="font-size: 1.2rem; opacity: 0.7;">
                Generating questions from the void<span class="dots">...</span>
            </div>
        </div>
    `;
    
    document.body.appendChild(introOverlay);
    
    // Animate text lines
    const lines = introOverlay.querySelectorAll('.intro-line');
    lines.forEach((line, index) => {
        const delay = parseInt(line.getAttribute('data-delay'));
        setTimeout(() => {
            line.classList.add('visible');
        }, delay);
    });
    
    // Start image slideshow
    let currentImageIndex = 0;
    const images = introOverlay.querySelectorAll('.intro-bg-image');
    const slideInterval = setInterval(() => {
        images[currentImageIndex].classList.remove('active');
        currentImageIndex = (currentImageIndex + 1) % images.length;
        images[currentImageIndex].classList.add('active');
    }, 2000);
    
    // Wait for quiz to load and minimum duration
    const MINIMUM_DURATION = 3000; // 3 seconds minimum for slideshow
    const startTime = Date.now();
    
    Promise.all([
        quizLoadPromise,
        new Promise(resolve => setTimeout(resolve, MINIMUM_DURATION))
    ]).then(([quizData]) => {
        console.log('[DEBUG] ✅ Quiz and minimum duration complete');
        console.log('[DEBUG] Quiz data received:', quizData ? 'YES' : 'NO');
        clearInterval(slideInterval);
        
        // Show text intro BEFORE fading out slideshow to prevent showing main site
        showHorrorTextIntro(movieTitle, quizData);
        
        // Then fade out and remove slideshow
        introOverlay.classList.add('intro-fade-out');
        setTimeout(() => {
            introOverlay.remove();
        }, 1500);
    }).catch((error) => {
        console.error('❌ Error in slideshow preload:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        clearInterval(slideInterval);
        introOverlay.remove();
        showHorrorTextIntro(movieTitle, null);
    });
}

// Preload quiz data during slideshow - NOW USES UNIFIED startQuiz() FUNCTION
// UPDATED: Uses unified startQuiz() to ensure all quizzes come from LangChain
async function preloadQuizData(movieTitle) {
    try {
        // Get user info
        const savedUser = localStorage.getItem('horrorUser');
        let userId = 'guest';
        if (savedUser) {
            try {
                const userObject = JSON.parse(savedUser);
                userId = userObject.sub || userObject.email || 'guest';
            } catch (e) {
                console.error('Error parsing user:', e);
            }
        }
        
        console.log('[LANGCHAIN QUIZ] 🔮 Preloading quiz data using unified startQuiz()...');
        
        // Use unified startQuiz() function - always fetches from LangChain
        const quizData = await startQuiz(userId, movieTitle);
        
        console.log('[LANGCHAIN QUIZ] ✅ Quiz preloaded:', quizData.questions.length, 'questions');
        
        return quizData;
    } catch (error) {
        console.error('❌ Error preloading Oracle quiz data:', error);
        console.error('Error details:', error.message);
        
        if (error.name === 'AbortError') {
            console.error('⏱️ Request timed out after 30 seconds');
            console.error('');
            console.error('⚠️ POSSIBLE CAUSES:');
            console.error('   1. Backend server is not running');
            console.error('   2. OpenAI API is slow or not responding');
            console.error('   3. Network connectivity issues');
            console.error('');
            console.error('💡 TO FIX:');
            console.error('   - Make sure backend is running: python app.py');
            console.error('   - Or run: RUN_BACKEND.bat');
            console.error('   - Check that you see "Running on http://localhost:5000"');
        } else if (error.message && error.message.includes('Failed to fetch')) {
            console.error('');
            console.error('⚠️ BACKEND NOT RUNNING!');
            console.error('   The backend server at http://localhost:5000 is not responding.');
            console.error('');
            console.error('💡 TO START BACKEND:');
            console.error('   1. Double-click RUN_BACKEND.bat');
            console.error('   2. Or run: python app.py');
            console.error('   3. Wait for "Running on http://localhost:5000"');
            console.error('   4. Refresh this page');
        }
        
        return null;
    }
}

// NEW: Show horror text intro with login options
function showHorrorTextIntro(movieTitle, quizData) {
    // Create horror text intro overlay
    const textIntro = document.createElement('div');
    textIntro.id = 'horror-text-intro';
    
    textIntro.innerHTML = `
        <div class="horror-intro-bg-effect"></div>
        <div class="horror-intro-content">
            <h1 class="horror-intro-title">Face Your Nightmares</h1>
            <p class="horror-intro-text">You have awakened a gateway to darker worlds — where only your mind decides your fate.</p>
            <p class="horror-intro-text">Survive each quiz to save your soul... or be claimed by the darkness.</p>
            <p class="horror-intro-text">Sign in with Google (recommended) to keep your progress and unlock hidden paths.</p>
            <p class="horror-intro-text">Or continue without login... if you dare.</p>
            <div class="horror-intro-buttons">
                <button class="horror-intro-btn google-signin" onclick="handleGoogleLogin('${movieTitle}', ${JSON.stringify(quizData).replace(/"/g, '&quot;')})">
                    Sign in with Google
                </button>
                <button class="horror-intro-btn continue-without" onclick="continueWithoutLogin('${movieTitle}', ${JSON.stringify(quizData).replace(/"/g, '&quot;')})">
                    Continue Without Login
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(textIntro);
    
    // Store quiz data globally for button handlers
    window.pendingQuizData = quizData;
    window.pendingMovieTitle = movieTitle;
}

// NEW: Handle Google login from intro screen
function handleGoogleLogin(movieTitle, quizData) {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('horrorUser');
    
    if (savedUser) {
        // Remove the text intro overlay FIRST to prevent z-index blocking
        const textIntro = document.getElementById('horror-text-intro');
        if (textIntro) {
            textIntro.classList.add('horror-text-intro-fade-out');
            setTimeout(() => {
                textIntro.remove();
            }, 500);
        }
        
        // User is already logged in, proceed to quiz immediately
        proceedToQuiz(window.pendingMovieTitle, window.pendingQuizData);
    } else {
        // Store pending quiz data so handleCredentialResponse can continue after login
        window.pendingMovieTitle = movieTitle;
        window.pendingQuizData = quizData;
        
        // Try to trigger the header Google Sign-In button
        const headerGoogleBtn = document.getElementById('google-login-btn');
        if (headerGoogleBtn && headerGoogleBtn.querySelector('div[role="button"]')) {
            // Scroll to top so user can see the sign-in process
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Highlight the header button
            headerGoogleBtn.style.transition = 'all 0.3s';
            headerGoogleBtn.style.transform = 'scale(1.1)';
            headerGoogleBtn.style.boxShadow = '0 0 20px rgba(255, 255, 0, 0.8)';
            
            // Click the Google Sign-In button after a brief moment
            setTimeout(() => {
                const googleButton = headerGoogleBtn.querySelector('div[role="button"]');
                if (googleButton) {
                    googleButton.click();
                }
                // Reset highlight after click
                setTimeout(() => {
                    headerGoogleBtn.style.transform = '';
                    headerGoogleBtn.style.boxShadow = '';
                }, 1000);
            }, 500);
        } else if (typeof google !== 'undefined' && google.accounts && google.accounts.id) {
            // Fallback: Try to show the Google One Tap prompt
            google.accounts.id.prompt((notification) => {
                if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
                    // One Tap couldn't be shown, show message
                    showLoginMessage();
                }
            });
        } else {
            // Google Sign-In not initialized yet, show message
            showLoginMessage();
        }
    }
}

// Helper function to show login message
function showLoginMessage() {
    const textIntro = document.getElementById('horror-text-intro');
    if (!textIntro) return;
    
    const content = textIntro.querySelector('.horror-intro-content');
    if (!content) return;
    
    // Check if message already exists
    if (content.querySelector('.login-help-message')) return;
    
    const helpMsg = document.createElement('p');
    helpMsg.className = 'horror-intro-text text-yellow-400 font-bold login-help-message';
    helpMsg.style.marginTop = '2rem';
    helpMsg.innerHTML = '⚠️ Please click the <strong>"Sign in with Google"</strong> button in the header at the top of the page, then return here to continue your quest.';
    content.appendChild(helpMsg);
    
    // Highlight the header button briefly
    const headerGoogleBtn = document.getElementById('google-login-btn');
    if (headerGoogleBtn) {
        headerGoogleBtn.style.transition = 'all 0.3s';
        headerGoogleBtn.style.transform = 'scale(1.2)';
        headerGoogleBtn.style.boxShadow = '0 0 20px rgba(255, 255, 0, 0.8)';
        setTimeout(() => {
            headerGoogleBtn.style.transform = '';
            headerGoogleBtn.style.boxShadow = '';
        }, 2000);
    }
}

// NEW: Continue without login
function continueWithoutLogin(movieTitle, quizData) {
    // Remove the text intro overlay FIRST to prevent z-index blocking
    const textIntro = document.getElementById('horror-text-intro');
    if (textIntro) {
        textIntro.classList.add('horror-text-intro-fade-out');
        setTimeout(() => {
            textIntro.remove();
        }, 500);
    }
    
    // Start the quiz IMMEDIATELY
    proceedToQuiz(window.pendingMovieTitle, window.pendingQuizData);
}

// NEW: Proceed to quiz (unified entry point from intro screen)
function proceedToQuiz(movieTitle, quizData) {
    console.log('[DEBUG] proceedToQuiz called with:', { movieTitle, quizData });
    console.log('[DEBUG] quizData.questions:', quizData ? quizData.questions : 'quizData is null');
    
    if (quizData && quizData.questions && quizData.questions.length > 0) {
        // Use preloaded data
        console.log('[DEBUG] Using preloaded quiz data');
        showQuizModalWithData(movieTitle, quizData);
    } else {
        // Fallback: show modal and load quiz
        console.log('[DEBUG] Fallback - loading quiz via startQuizModal');
        startQuizModal(movieTitle);
    }
}

// Show quiz modal with preloaded data
function showQuizModalWithData(movieTitle, quizData) {
    const modal = document.createElement('div');
    modal.id = 'bloodQuizModal';
    modal.className = 'fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center';
    modal.style.zIndex = '9999'; // Ensure it's above all other overlays including horror-text-intro (z-index: 5001)
    
    // Use preloaded quiz data or get from localStorage as fallback
    const nextQuizNumber = quizData ? quizData.nextQuizNumber : (JSON.parse(localStorage.getItem('horror-quiz-history') || '[]').length + 1);
    
    modal.innerHTML = `
        <div class="bg-gradient-to-b from-red-950 via-black to-red-950 border-4 border-red-800 rounded-lg max-w-2xl w-11/12 p-8 shadow-2xl relative">
            <button onclick="closeBloodQuiz()" 
                    class="absolute top-4 right-4 text-red-400 hover:text-white text-3xl font-bold transition-colors">
                ✕
            </button>
            
            <div class="text-center mb-6">
                <h2 class="text-4xl font-bold text-red-500 mb-2" style="text-shadow: 0 0 20px rgba(255, 0, 0, 0.8);">
                    Blood QUIZ 🩸 you can cry but no n one hears you
                </h2>
                <p class="text-gray-400" id="quiz-subtitle">
                    ${nextQuizNumber === 1 ? 'Discovering your horror DNA...' : `Quiz #${nextQuizNumber} - Evolving based on your answers...`}
                </p>
                <div id="quiz-theme-display" class="mt-2 text-sm text-red-300"></div>
            </div>
            
            <div id="quizContent" class="min-h-[300px]">
                <!-- Quiz content will be inserted here -->
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // If we have preloaded data, use it directly. Otherwise, load it now
    if (quizData && quizData.questions && quizData.questions.length > 0) {
        displayQuizWithData(quizData);
    } else {
        startAdaptiveQuiz(movieTitle);
    }
}

function startQuizModal(movieTitle) {
    // This is used when skipping the intro
    showQuizModalWithData(movieTitle, null);
}

// Display quiz using preloaded data
async function displayQuizWithData(quizData) {
    const quizContent = document.getElementById('quizContent');
    if (!quizContent) return;
    
    console.log('[DEBUG] displayQuizWithData called with:', quizData);
    
    // Helper to normalize question formats coming from different backends (Oracle/Legacy)
    function normalizeQuizQuestions(questions) {
        if (!Array.isArray(questions)) return [];
        return questions.map((q) => {
            const questionText = q.question || q.q || q.text || '';
            const options = q.options || q.a || q.choices || [];
            let correctIndex = typeof q.correct === 'number' ? q.correct : (
                typeof q.correct_index === 'number' ? q.correct_index : -1
            );
            if (correctIndex === -1 && q.correct_answer && Array.isArray(options)) {
                const target = String(q.correct_answer).trim().toLowerCase();
                correctIndex = options.findIndex((opt) => String(opt).trim().toLowerCase() === target);
            }
            return {
                question: questionText,
                options: options,
                correct: correctIndex,
                is_profile: q.is_profile || false
            };
        });
    }

    // Set quiz data from preloaded content (normalized)
    // Validate quizData before accessing properties
    if (!quizData) {
        console.error('❌ CRITICAL ERROR: quizData is undefined in displayQuizWithData!');
        alert('⚠️ Quiz data failed to load. Please try again.');
        closeBloodQuiz();
        return;
    }
    
    currentQuiz.questions = normalizeQuizQuestions(quizData.questions || []);
    currentQuiz.currentQuestion = 0;
    currentQuiz.score = 0;
    currentQuiz.quizNumber = quizData.nextQuizNumber;
    currentQuiz.theme = quizData.theme;
    currentQuiz.difficulty = quizData.difficulty;
    currentQuiz.answers = [];
    currentQuiz.profileAnswers = [];
    currentQuiz.oracleData = quizData.oracleData || null;  // Store for Oracle submission
    
    // Enable Oracle mode if we have Oracle data
    if (quizData.oracleData) {
        oracleState.isOracleMode = true;
        const savedUser = localStorage.getItem('horrorUser');
        if (savedUser) {
            try {
                const userObject = JSON.parse(savedUser);
                oracleState.userId = userObject.sub || userObject.email || 'guest';
            } catch (e) {
                oracleState.userId = 'guest';
            }
        }
        
        // Update fear level if available
        if (quizData.oracleData.player_profile && quizData.oracleData.player_profile.fear_level) {
            oracleState.fearLevel = quizData.oracleData.player_profile.fear_level;
        }
    }
    
    console.log('[DEBUG] currentQuiz.questions:', currentQuiz.questions);
    console.log('[DEBUG] questions length:', currentQuiz.questions ? currentQuiz.questions.length : 'undefined');
    console.log('[DEBUG] Oracle mode:', oracleState.isOracleMode);
    
    // Display theme
    const themeDisplay = document.getElementById('quiz-theme-display');
    if (themeDisplay) {
        themeDisplay.innerHTML = `
            <span class="inline-block px-3 py-1 bg-red-900 rounded-full text-xs">
                ${currentQuiz.theme} • ${currentQuiz.difficulty}
            </span>
        `;
    }
    
    // Verify we have valid questions
    if (!currentQuiz.questions || currentQuiz.questions.length === 0) {
        console.error('❌ CRITICAL ERROR: No questions in currentQuiz after displayQuizWithData setup!');
        console.error('quizData:', quizData);
        alert('⚠️ Quiz failed to load questions. Please try again.');
        closeBloodQuiz();
        return;
    }
    
    console.log('[DEBUG] ✅ Questions validated:', currentQuiz.questions.length, 'questions available');
    console.log('[DEBUG] First question preview:', currentQuiz.questions[0]);
    
    // If Oracle mode is enabled, show Oracle intro with BEGIN THE TRIAL button
    if (oracleState.isOracleMode && quizData && quizData.oracleData) {
        console.log('[DEBUG] Showing Oracle intro with BEGIN THE TRIAL button');
        showOracleIntroInModal(quizData.oracleData);
    } else {
        // Regular quiz mode - start showing questions immediately
        console.log('[DEBUG] Starting regular quiz mode');
        showQuestion();
    }
}

/**
 * Show Oracle intro with BEGIN THE TRIAL button in the blood quiz modal
 */
function showOracleIntroInModal(oracleData) {
    // Use quizContent (from bloodQuizModal) instead of quizBody
    const quizContent = document.getElementById('quizContent');
    if (!quizContent) {
        console.error('quizContent not found!');
        return;
    }
    
    // Show Oracle's intro with lore
    const intro = oracleData.intro || 'The Oracle awaits your challenge...';
    const room = oracleData.room || 'The First Chamber';
    const lore = oracleData.lore || {};
    
    // Log unique chamber for debugging
    console.log(`🎃 New Chamber: ${room}`);
    console.log(`📋 Quiz Theme: ${oracleData.theme || 'general_horror'}`);
    console.log(`⚡ Difficulty: ${oracleData.difficulty || 'intermediate'}`);
    
    quizContent.innerHTML = `
        <div class="oracle-intro-container">
            <h1 class="oracle-main-title" id="oracleMainTitle">THE ORACLE'S TRIAL</h1>
            <div class="oracle-room-title">
                ${room}
            </div>
            <div class="oracle-intro-text">
                ${intro}
            </div>
            ${lore.whisper ? `
                <div class="oracle-lore-whisper" style="color: #999; font-style: italic; font-size: 0.95rem; margin: 1rem 0 2rem; border-left: 3px solid #b91c1c; padding-left: 1rem; max-width: 700px;">
                    ${lore.whisper}
                </div>
            ` : ''}
            <button onclick="startOracleQuestion()" class="oracle-begin-btn">
                ENTER NIGHTMARE
            </button>
        </div>
    `;
    
    // Start blood drip animation after a short delay
    setTimeout(() => {
        spawnBloodDrips();
        // Continue spawning drips periodically
        setInterval(spawnBloodDrips, 3000);
    }, 500);
}

/**
 * Spawn blood drips from random positions under the title
 */
function spawnBloodDrips() {
    const titleElement = document.getElementById('oracleMainTitle');
    if (!titleElement) return;
    
    const container = titleElement.closest('.oracle-intro-container');
    if (!container) return;
    
    const titleRect = titleElement.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    
    // Create 3-5 blood drips at random positions
    const dripCount = Math.floor(Math.random() * 3) + 3;
    
    for (let i = 0; i < dripCount; i++) {
        const drip = document.createElement('div');
        drip.className = 'blood-drip';
        
        // Random position along the title width
        const randomX = titleRect.left - containerRect.left + Math.random() * titleRect.width;
        const startY = titleRect.bottom - containerRect.top;
        
        drip.style.left = `${randomX}px`;
        drip.style.top = `${startY}px`;
        
        container.appendChild(drip);
        
        // Remove the drip after animation completes
        setTimeout(() => {
            drip.remove();
        }, 2500);
    }
}

function closeBloodQuiz() {
    const modal = document.getElementById('bloodQuizModal');
    if (modal) {
        modal.remove();
        currentQuiz = {
            questions: [],
            currentQuestion: 0,
            score: 0,
            category: 'general',
            quizNumber: 1,
            theme: '',
            difficulty: '',
            answers: [],
            profileAnswers: [],
            oracleData: null
        };
        
        // Reset Oracle state
        oracleState.isOracleMode = false;
        oracleState.fearLevel = 50;
        
        // Clear blood drip interval
        if (window.oracleDripInterval) {
            clearInterval(window.oracleDripInterval);
            window.oracleDripInterval = null;
        }
        
        // Remove fear level styling
        document.body.classList.remove('fear-low', 'fear-medium', 'fear-high', 'fear-extreme');
    }
}

// ===== AI-ADAPTIVE QUIZ SYSTEM - UPDATED TO USE UNIFIED startQuiz() =====
// UPDATED: Now uses unified startQuiz() to ensure all quizzes come from LangChain
async function startAdaptiveQuiz(movieTitle = null) {
    const quizContent = document.getElementById('quizContent');
    if (!quizContent) return;
    
    // Show enhanced loading message with progress
    quizContent.innerHTML = `
        <div class="text-center text-red-400">
            <div class="mb-4 text-4xl animate-pulse">🔮</div>
            <p class="mb-2 text-xl font-bold text-shadow">The Oracle stirs...</p>
            <div class="mb-4 text-sm text-gray-400 italic">Summoning questions from LangChain...</div>
            <div class="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                <div id="quiz-load-progress" class="h-full bg-red-600 transition-all duration-500" style="width: 0%"></div>
            </div>
            <div class="mt-2 text-xs text-gray-500">This may take a few seconds...</div>
        </div>
    `;
    
    // Animate progress bar
    const progressBar = document.getElementById('quiz-load-progress');
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress = Math.min(progress + 5, 90);
        if (progressBar) progressBar.style.width = progress + '%';
    }, 150);
    
    try {
        // Get user info
        const savedUser = localStorage.getItem('horrorUser');
        const userId = savedUser ? JSON.parse(savedUser).sub : null;
        
        console.log('[LANGCHAIN QUIZ] ⏱️  Fetching quiz from LangChain...');
        const fetchStart = performance.now();
        
        // Use unified startQuiz() function - always fetches from LangChain
        const quizData = await startQuiz(userId, movieTitle);
        
        const fetchEnd = performance.now();
        console.log(`[LANGCHAIN QUIZ] ⏱️  Fetch completed in ${((fetchEnd - fetchStart) / 1000).toFixed(2)}s`);
        
        // Validate quizData before proceeding
        if (!quizData) {
            throw new Error('Quiz data is undefined');
        }
        
        // Complete progress bar
        clearInterval(progressInterval);
        if (progressBar) progressBar.style.width = '100%';

        // Set quiz data from unified function
        currentQuiz.questions = quizData.questions || [];
        currentQuiz.currentQuestion = 0;
        currentQuiz.score = 0;
        currentQuiz.quizNumber = quizData.nextQuizNumber;
        currentQuiz.theme = quizData.theme || 'Horror';
        currentQuiz.difficulty = quizData.difficulty || 'Medium';
        currentQuiz.answers = [];
        currentQuiz.profileAnswers = [];
        currentQuiz.oracleData = quizData.oracleData || null;  // Store for submission
        
        // Enable Oracle mode
        oracleState.isOracleMode = true;
        oracleState.userId = userId || 'guest';
        
        // Display theme
        const themeDisplay = document.getElementById('quiz-theme-display');
        if (themeDisplay) {
            themeDisplay.innerHTML = `
                <span class="inline-block px-3 py-1 bg-red-900 rounded-full text-xs">
                    ${currentQuiz.theme} • ${currentQuiz.difficulty}
                </span>
            `;
        }
        
        // Show immersive message if provided
        if (quizData.intro) {
            await showImmersiveMessage(quizData.intro);
        }
        
        // Start showing questions
        showQuestion();
        
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Error loading adaptive quiz:', error);
        
        // Better error handling with retry option
        clearInterval(progressInterval);
        const errorMsg = error.message || 'The Oracle encountered an error';
        
        quizContent.innerHTML = `
            <div class="text-center text-red-400">
                <div class="mb-4 text-4xl">⚠️</div>
                <p class="mb-2 font-bold">${errorMsg}</p>
                <p class="mb-4 text-sm text-gray-500">Failed to load quiz from LangChain backend</p>
                <div class="flex gap-2 justify-center">
                    <button onclick="startAdaptiveQuiz()" 
                            class="px-4 py-2 bg-red-700 text-white rounded hover:bg-red-600 transition">
                        🔄 Retry
                    </button>
                    <button onclick="closeBloodQuiz()" 
                            class="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition">
                        Close
                    </button>
                </div>
            </div>
        `;
    }
}

async function showImmersiveMessage(message) {
    const quizContent = document.getElementById('quizContent');
    if (!quizContent) return;
    
    quizContent.innerHTML = `
        <div class="text-center">
            <div class="mb-6 text-6xl animate-pulse">👁️</div>
            <p class="text-xl text-red-400 font-bold mb-4" style="text-shadow: 0 0 20px rgba(255,0,0,0.8);">
                ${message}
            </p>
            <div class="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                <div class="h-full bg-red-600 animate-pulse" style="width: 100%; animation: pulse 1.5s infinite;"></div>
            </div>
        </div>
    `;
    
    // Wait 2 seconds before continuing
    await new Promise(resolve => setTimeout(resolve, 2000));
}

/**
 * ===== UNIFIED QUIZ START FUNCTION =====
 * This function replaces all old static/cached quiz initialization.
 * It ALWAYS fetches dynamic LangChain-generated quiz data from /api/start_quiz.
 * 
 * DATA FLOW: Frontend → POST /api/start_quiz → LangChain Builder → Returns JSON → Frontend Renders
 * 
 * @param {string} userId - User ID (from Google OAuth or 'guest')
 * @param {string} movieTitle - Optional movie title context
 * @returns {Promise<Object>} Quiz data with questions, theme, difficulty, intro, room, lore
 */
async function startQuiz(userId = null, movieTitle = null) {
    console.log('[LANGCHAIN QUIZ] 🎯 Starting dynamic quiz from /api/start_quiz endpoint');
    
    // Get user ID from localStorage if not provided
    if (!userId) {
        const savedUser = localStorage.getItem('horrorUser');
        if (savedUser) {
            try {
                const userObject = JSON.parse(savedUser);
                userId = userObject.sub || userObject.email || 'guest';
            } catch (e) {
                console.error('Error parsing user:', e);
                userId = 'guest';
            }
        } else {
            userId = 'guest';
        }
    }
    
    // Prepare request body for backend API
    const requestBody = {
        user_id: userId,
        force_new: true  // Always generate fresh questions from LangChain
    };
    
    // Use stored next difficulty and theme from previous quiz evaluation if available
    if (oracleState.nextDifficulty) {
        requestBody.difficulty = oracleState.nextDifficulty;
        console.log(`[LANGCHAIN QUIZ] 🎯 Using recommended difficulty: ${oracleState.nextDifficulty}`);
    }
    if (oracleState.nextTheme) {
        requestBody.theme = oracleState.nextTheme;
        console.log(`[LANGCHAIN QUIZ] 🎨 Using recommended theme: ${oracleState.nextTheme}`);
    }
    
    try {
        // Call Flask backend → LangChain Oracle Engine
        const response = await fetch(`${API_BASE}/api/start_quiz`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const quizData = await response.json();
        
        // Validate quiz data
        if (!quizData || !quizData.questions || quizData.questions.length === 0) {
            throw new Error('Invalid quiz data: No questions received from LangChain');
        }
        
        console.log(`[LANGCHAIN QUIZ] ✅ Quiz loaded: ${quizData.questions.length} questions`);
        console.log(`[LANGCHAIN QUIZ] 📋 Theme: ${quizData.theme || 'unknown'} | ⚡ Difficulty: ${quizData.difficulty || 'unknown'}`);
        console.log(`[LANGCHAIN QUIZ] 🎃 Room: ${quizData.room || 'Unknown Chamber'}`);
        
        // Transform Oracle Engine format to frontend format
        const transformedQuestions = (quizData.questions || []).map(q => {
            const questionText = q.question || q.q || q.text || '';
            const options = q.options || q.a || q.choices || [];
            
            // Find correct answer index
            let correctIndex = typeof q.correct === 'number' ? q.correct : (
                typeof q.correct_index === 'number' ? q.correct_index : -1
            );
            
            if (correctIndex === -1 && q.correct_answer && Array.isArray(options)) {
                const target = String(q.correct_answer).trim().toLowerCase();
                correctIndex = options.findIndex((opt) => String(opt).trim().toLowerCase() === target);
            }
            
            if (correctIndex < 0) correctIndex = 0; // Default fallback
            
            return {
                question: questionText,
                options: options,
                correct: correctIndex,
                is_profile: q.is_profile || false
            };
        });
        
        // Get quiz history for numbering
        const quizHistory = JSON.parse(localStorage.getItem('horror-quiz-history') || '[]');
        const nextQuizNumber = quizHistory.length + 1;
        
        // Return normalized quiz data
        return {
            questions: transformedQuestions,
            theme: quizData.theme || 'Horror Oracle',
            difficulty: quizData.difficulty || 'intermediate',
            nextQuizNumber: nextQuizNumber,
            oracleData: quizData,  // Store full Oracle Engine response for submission
            room: quizData.room,
            intro: quizData.intro,
            lore: quizData.lore,
            player_profile: quizData.player_profile,
            oracle_state: quizData.oracle_state
        };
        
    } catch (error) {
        console.error('[LANGCHAIN QUIZ] ❌ Error fetching quiz:', error);
        throw error;
    }
}

/**
 * ===== DEPRECATED: STATIC QUIZ FUNCTION =====
 * This function is DISABLED - all quizzes now come from LangChain via /api/start_quiz
 * Keeping for reference only - DO NOT USE - use startQuiz() instead
 */
function getQuizQuestions_DEPRECATED(category, movieTitle) {
    console.warn('[DEPRECATED] getQuizQuestions() called - using static data. Use startQuiz() instead!');
    const questionPools = {
        general: [
            { q: "What year was The Exorcist released?", a: ["1973", "1975", "1971", "1969"], correct: 0 },
            { q: "Who directed Halloween (1978)?", a: ["Wes Craven", "John Carpenter", "Tobe Hooper", "George Romero"], correct: 1 },
            { q: "What is the name of the possessed doll in Child's Play?", a: ["Billy", "Tommy", "Chucky", "Johnny"], correct: 2 },
            { q: "In which film does 'They're here' appear?", a: ["The Shining", "Halloween", "Poltergeist", "The Ring"], correct: 2 },
            { q: "What is the name of the camp in Friday the 13th?", a: ["Camp Crystal Lake", "Camp Blackwater", "Camp Arawak", "Camp Redwood"], correct: 0 }
        ],
        slashers: [
            { q: "What mask does Jason wear?", a: ["William Shatner", "Hockey Mask", "Leather Face", "White Mask"], correct: 1 },
            { q: "How many kills in Friday the 13th (1980)?", a: ["8", "10", "12", "13"], correct: 1 },
            { q: "What's Michael Myers' middle name?", a: ["James", "Audrey", "Thomas", "Andrew"], correct: 1 },
            { q: "Who is Ghostface in the first Scream?", a: ["Billy", "Stu", "Billy & Stu", "Sidney"], correct: 2 },
            { q: "What weapon does Freddy Krueger use?", a: ["Machete", "Chainsaw", "Glove with Knives", "Axe"], correct: 2 }
        ],
        cult: [
            { q: "Who directed The Wicker Man (1973)?", a: ["Robin Hardy", "Nicolas Roeg", "Ken Russell", "Michael Reeves"], correct: 0 },
            { q: "What film features 'Heather, Heather, and Heather'?", a: ["The Craft", "Heathers", "Jennifer's Body", "Carrie"], correct: 1 },
            { q: "Complete: 'Shop smart, shop...'", a: ["K-Mart", "S-Mart", "E-Mart", "Q-Mart"], correct: 1 },
            { q: "What is the Tall Man's weapon in Phantasm?", a: ["Silver Sphere", "Chainsaw", "Hook", "Knife"], correct: 0 },
            { q: "Who made Suspiria (1977)?", a: ["Lucio Fulci", "Mario Bava", "Dario Argento", "Umberto Lenzi"], correct: 2 }
        ],
        eighties: [
            { q: "What year did Nightmare on Elm Street debut?", a: ["1982", "1984", "1986", "1988"], correct: 1 },
            { q: "Who played Pinhead in Hellraiser?", a: ["Doug Bradley", "Robert Englund", "Kane Hodder", "Tony Todd"], correct: 0 },
            { q: "The Thing (1982) is set where?", a: ["Alaska", "Canada", "Antarctica", "Greenland"], correct: 2 },
            { q: "What grows out of the drain in Poltergeist?", a: ["A Tree", "A Hand", "A Snake", "Hair"], correct: 0 },
            { q: "Return of the Living Dead introduced what zombie trait?", a: ["Running", "Talking", "Eating Brains", "Swimming"], correct: 2 }
        ],
        classics: [
            { q: "Who played Dracula in 1931?", a: ["Lon Chaney", "Boris Karloff", "Bela Lugosi", "Vincent Price"], correct: 2 },
            { q: "What year was Frankenstein released?", a: ["1929", "1931", "1933", "1935"], correct: 1 },
            { q: "Who directed Psycho?", a: ["William Castle", "Alfred Hitchcock", "Roger Corman", "James Whale"], correct: 1 },
            { q: "The Cabinet of Dr. Caligari is from which country?", a: ["USA", "UK", "France", "Germany"], correct: 3 },
            { q: "What was the first zombie film?", a: ["White Zombie", "I Walked with a Zombie", "Night of the Living Dead", "Dawn of the Dead"], correct: 0 }
        ],
        creatures: [
            { q: "What is the creature in The Descent?", a: ["Wendigos", "Crawlers", "Cave Dwellers", "Morlocks"], correct: 1 },
            { q: "Who directed The Host (2006)?", a: ["Park Chan-wook", "Bong Joon-ho", "Kim Ji-woon", "Na Hong-jin"], correct: 1 },
            { q: "What awakens the Graboids in Tremors?", a: ["Drilling", "Explosions", "Vibrations", "Heat"], correct: 2 },
            { q: "The Ritual features which creature?", a: ["Wendigo", "Jotunn", "Draugr", "Bergsra"], correct: 1 },
            { q: "What is the creature in Jeepers Creepers called?", a: ["The Creeper", "The Reaper", "The Keeper", "The Sleeper"], correct: 0 }
        ],
        possession: [
            { q: "What is Regan's imaginary friend called?", a: ["Mr. Howdy", "Captain Howdy", "Father Howdy", "Doctor Howdy"], correct: 1 },
            { q: "The demon in Insidious is from where?", a: ["Hell", "The Further", "The Upside Down", "The Dark Place"], correct: 1 },
            { q: "What starts the possession in Evil Dead?", a: ["Ouija Board", "Necronomicon", "Séance", "Mirror"], correct: 1 },
            { q: "Who directed The Conjuring?", a: ["James Wan", "Leigh Whannell", "Mike Flanagan", "Ari Aster"], correct: 0 },
            { q: "What does the Dybbuk Box contain?", a: ["A Spirit", "A Demon", "A Dybbuk", "A Soul"], correct: 2 }
        ],
        jhorror: [
            { q: "How many days to live after watching The Ring tape?", a: ["3", "5", "7", "13"], correct: 2 },
            { q: "What is the ghost called in The Grudge?", a: ["Sadako", "Kayako", "Tomie", "Yuki"], correct: 1 },
            { q: "Who directed the original Ringu?", a: ["Hideo Nakata", "Takashi Shimizu", "Takashi Miike", "Kiyoshi Kurosawa"], correct: 0 },
            { q: "What film features the Slit-Mouthed Woman?", a: ["Carved", "Cursed", "Scream", "Slash"], correct: 0 },
            { q: "Dark Water features what haunted object?", a: ["TV", "Phone", "Elevator", "Water Tank"], correct: 3 }
        ],
        impossible: [
            { q: "What was The Blair Witch Project's budget?", a: ["$22,000", "$60,000", "$100,000", "$250,000"], correct: 1 },
            { q: "How many gallons of blood in Evil Dead (1981)?", a: ["50", "100", "200", "300"], correct: 2 },
            { q: "What cereal appears in Halloween (1978)?", a: ["Cheerios", "Corn Flakes", "Lucky Charms", "Frosted Flakes"], correct: 1 },
            { q: "How long did The Exorcist's pea soup take to make?", a: ["2 days", "4 days", "7 days", "10 days"], correct: 0 },
            { q: "What was Jason's original name going to be?", a: ["Josh", "Jake", "Jerry", "Jack"], correct: 0 }
        ]
    };
    
    const pool = questionPools[category] || questionPools.general;
    return pool.sort(() => 0.5 - Math.random()).slice(0, 5);
}

// Fetch movie-specific quiz questions from backend and normalize format
async function loadMovieQuizQuestions(movieTitle) {
    try {
        const resp = await fetch(`${API_BASE}/quiz?movie=${encodeURIComponent(movieTitle)}`);
        const data = await resp.json();
        const raw = data && data.questions;
        if (!Array.isArray(raw)) return [];

        const mapped = [];
        for (const item of raw) {
            const questionText = item.question || item.q;
            const options = item.options || item.a;
            let answer = item.answer;
            if (!questionText || !Array.isArray(options) || options.length < 2) continue;

            let correctIndex = 0;
            if (typeof answer === 'string') {
                const letter = answer.trim().toUpperCase();
                const letterIdx = 'ABCD'.indexOf(letter);
                if (letterIdx >= 0 && options[letterIdx] !== undefined) {
                    correctIndex = letterIdx;
                } else {
                    const idx = options.findIndex(o => String(o).trim().toLowerCase() === answer.trim().toLowerCase());
                    if (idx >= 0) correctIndex = idx;
                }
            } else if (typeof answer === 'number' && answer >= 0 && answer < options.length) {
                correctIndex = answer;
            } else if (typeof item.correct === 'number') {
                correctIndex = item.correct;
            }

            mapped.push({ q: questionText, a: options, correct: correctIndex });
        }

        return mapped.slice(0, 5);
    } catch (e) {
        console.error('Quiz fetch error:', e);
        return [];
    }
}

// Build simple movie-specific questions from known details as a fallback
function generateFallbackMovieQuestions(movieTitle) {
    const details = currentMovieDetails || {};
    const questions = [];

    function shuffleWithCorrectFirst(options, correctValue) {
        const arr = [...options];
        // put correct at random index
        const correctIdx = Math.floor(Math.random() * arr.length);
        const correctPos = arr.findIndex(o => String(o) === String(correctValue));
        if (correctPos !== -1) {
            [arr[correctIdx], arr[correctPos]] = [arr[correctPos], arr[correctIdx]];
        }
        return { options: arr, correctIndex: correctIdx };
    }

    function uniqueSample(pool, count, exclude = new Set()) {
        const filtered = pool.filter(x => !exclude.has(String(x)));
        const out = [];
        while (out.length < count && filtered.length > 0) {
            const idx = Math.floor(Math.random() * filtered.length);
            out.push(filtered.splice(idx, 1)[0]);
        }
        return out;
    }

    // 1) Exact title question
    const decoyTitlesPool = [
        'Halloween', 'Scream', 'The Conjuring', 'It', 'The Exorcist', 'Poltergeist',
        'A Nightmare on Elm Street', 'Saw', 'Friday the 13th', 'Get Out', 'Midsommar',
        'Sinister', 'The Ring', 'Insidious', 'Candyman', 'The Babadook'
    ];
    const titleEx = new Set([movieTitle]);
    const titleDecoys = uniqueSample(decoyTitlesPool, 3, titleEx);
    if (titleDecoys.length === 3) {
        const all = [movieTitle, ...titleDecoys];
        const { options, correctIndex } = shuffleWithCorrectFirst(all, movieTitle);
        questions.push({ q: `Which of these is the exact title you searched?`, a: options, correct: correctIndex });
    }

    // 2) Year question
    if (details.year) {
        const year = parseInt(details.year, 10);
        if (!Number.isNaN(year)) {
            const decoys = new Set([String(year)]);
            const years = [];
            while (years.length < 3) {
                const delta = Math.floor(Math.random() * 6) + 1; // 1..6
                const sign = Math.random() < 0.5 ? -1 : 1;
                const candidate = String(year + sign * delta);
                if (!decoys.has(candidate)) {
                    decoys.add(candidate);
                    years.push(candidate);
                }
            }
            const all = [String(year), ...years];
            const { options, correctIndex } = shuffleWithCorrectFirst(all, String(year));
            questions.push({ q: `What year was "${movieTitle}" released?`, a: options, correct: correctIndex });
        }
    }

    // 3) Director question
    if (details.director) {
        const director = details.director;
        const directorPool = [
            'Wes Craven', 'John Carpenter', 'Tobe Hooper', 'George Romero', 'James Wan',
            'Ari Aster', 'Mike Flanagan', 'Sam Raimi', 'David Cronenberg', 'Jordan Peele'
        ];
        const decoys = uniqueSample(directorPool, 3, new Set([director]));
        if (decoys.length === 3) {
            const all = [director, ...decoys];
            const { options, correctIndex } = shuffleWithCorrectFirst(all, director);
            questions.push({ q: `Who directed "${movieTitle}"?`, a: options, correct: correctIndex });
        }
    }

    // 4) Genre question
    if (details.genres) {
        const parsed = String(details.genres).split(',').map(s => s.trim()).filter(Boolean);
        const mainGenre = parsed[0];
        if (mainGenre) {
            const genrePool = ['Horror', 'Thriller', 'Mystery', 'Comedy', 'Drama', 'Sci-Fi', 'Fantasy', 'Action'];
            const decoys = uniqueSample(genrePool, 3, new Set([mainGenre]));
            if (decoys.length === 3) {
                const all = [mainGenre, ...decoys];
                const { options, correctIndex } = shuffleWithCorrectFirst(all, mainGenre);
                questions.push({ q: `Which genre includes "${movieTitle}"?`, a: options, correct: correctIndex });
            }
        }
    }

    // 5) Rating question (if available)
    if (details.rating) {
        const ratingVal = parseFloat(details.rating);
        if (!Number.isNaN(ratingVal)) {
            const correct = ratingVal.toFixed(1);
            const decoySet = new Set([correct]);
            const decoys = [];
            while (decoys.length < 3) {
                const delta = (Math.floor(Math.random() * 5) + 1) / 10; // 0.1..0.5
                const sign = Math.random() < 0.5 ? -1 : 1;
                let candidateNum = Math.min(10, Math.max(0, ratingVal + sign * delta));
                const candidate = candidateNum.toFixed(1);
                if (!decoySet.has(candidate)) {
                    decoySet.add(candidate);
                    decoys.push(candidate);
                }
            }
            const all = [correct, ...decoys];
            const { options, correctIndex } = shuffleWithCorrectFirst(all, correct);
            questions.push({ q: `What is the rating of "${movieTitle}" (to 1 decimal)?`, a: options, correct: correctIndex });
        }
    }

    // Ensure at least 5 questions, add a title word question if needed
    while (questions.length < 5) {
        const words = String(movieTitle).split(/\s+/).map(w => w.replace(/[^\w']/g, '')).filter(w => w.length >= 3);
        const word = words.length > 0 ? words[Math.floor(Math.random() * words.length)] : movieTitle;
        const decoyWordPool = ['Night', 'Blood', 'Dark', 'Ghost', 'Fear', 'Death', 'Curse', 'Evil', 'Shadow', 'Mask'];
        const decoys = uniqueSample(decoyWordPool, 3, new Set([word]));
        const all = [word, ...decoys];
        const { options, correctIndex } = shuffleWithCorrectFirst(all, word);
        questions.push({ q: `Which of these words appears in the title "${movieTitle}"?`, a: options, correct: correctIndex });
    }

    return questions.slice(0, 5);
}

function showQuestion() {
    console.log('[DEBUG] ═══ showQuestion called ═══');
    
    // Support both quiz modal (quizBody) and blood quiz modal (quizContent)
    let quizContent = document.getElementById('quizBody') || document.getElementById('quizContent');
    
    console.log('[DEBUG] quizContent element found:', quizContent ? 'YES' : 'NO');
    console.log('[DEBUG] currentQuiz:', currentQuiz);
    console.log('[DEBUG] currentQuestion:', currentQuiz.currentQuestion);
    console.log('[DEBUG] total questions:', currentQuiz.questions ? currentQuiz.questions.length : 'UNDEFINED');
    
    if (!quizContent) {
        console.error('❌ CRITICAL: quizContent element not found!');
        alert('Quiz display error. Please close and try again.');
        return;
    }
    
    if (!currentQuiz.questions || currentQuiz.questions.length === 0) {
        console.error('❌ CRITICAL: No questions available!');
        alert('No questions loaded. Please close and try again.');
        return;
    }
    
    if (currentQuiz.currentQuestion >= currentQuiz.questions.length) {
        console.log('[DEBUG] Showing results - no more questions');
        
        // Check if Oracle mode - submit to Oracle instead of showing regular results
        if (oracleState.isOracleMode && currentQuiz.oracleData) {
            submitToOracle();
            return;
        }
        
        showQuizResults();
        return;
    }
    
    const question = currentQuiz.questions[currentQuiz.currentQuestion];
    
    if (!question) {
        console.error('❌ CRITICAL: Question at index', currentQuiz.currentQuestion, 'is undefined!');
        alert('Question data error. Please close and try again.');
        return;
    }
    
    const questionText = question.question || question.q;
    const options = question.options || question.a;
    const isProfile = question.is_profile || false;
    
    console.log('[DEBUG] ✅ Displaying question', currentQuiz.currentQuestion + 1);
    console.log('[DEBUG] Question text:', questionText);
    console.log('[DEBUG] Number of options:', options ? options.length : 0);
    console.log('[DEBUG] Full question object:', question);
    
    if (!questionText || !options || options.length === 0) {
        console.error('❌ CRITICAL: Question is missing text or options!');
        console.error('Question:', question);
        alert('Invalid question format. Please close and try again.');
        return;
    }
    
    const letters = ['A', 'B', 'C', 'D'];
    
    quizContent.innerHTML = `
        <div class="quiz-question">
            <p class="question-text">${questionText}</p>
            ${isProfile ? '<p class="text-yellow-400 text-xs text-center mb-3">🧬 PROFILE QUESTION - Your choice shapes your Horror DNA</p>' : ''}
            <div class="quiz-options">
                ${options.map((answer, index) => `
                    <div class="quiz-option" data-letter="${letters[index]}" onclick="checkAnswer(${index})">
                        ${answer}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Trigger blood drip animation for correct/wrong answers
function triggerBloodDrip(isCorrect) {
    const overlay = document.getElementById('blood-drip-overlay');
    if (!overlay) return;
    
    // Create multiple drips for more dramatic effect
    const dripCount = isCorrect ? 5 : 8; // More drips for wrong answers
    
    for (let i = 0; i < dripCount; i++) {
        setTimeout(() => {
            const drip = document.createElement('div');
            drip.className = isCorrect ? 'blood-drip-correct' : 'blood-drip-wrong';
            drip.style.position = 'absolute';
            drip.style.top = '0';
            drip.style.left = (Math.random() * 100) + '%';
            drip.style.width = isCorrect ? '4px' : '8px';
            drip.style.height = '60px';
            drip.style.animation = 'bloodDrip 1.8s ease-in forwards';
            overlay.appendChild(drip);
            
            // Remove drip after animation completes
            setTimeout(() => drip.remove(), 1800);
        }, i * 100); // Stagger the drips
    }
    
    // Add screen shake for wrong answers
    if (!isCorrect) {
        document.body.classList.add('shake');
        setTimeout(() => document.body.classList.remove('shake'), 600);
    }
}

function checkAnswer(answerIndex) {
    const question = currentQuiz.questions[currentQuiz.currentQuestion];
    const isCorrect = answerIndex === question.correct;
    
    // Trigger blood drip animation immediately
    triggerBloodDrip(isCorrect);
    
    // Get all answer options (divs with quiz-option class)
    const quizContent = document.getElementById('quizBody') || document.getElementById('quizContent');
    const options = quizContent.querySelectorAll('.quiz-option');
    
    // Disable all options to prevent multiple clicks
    options.forEach(opt => {
        opt.style.pointerEvents = 'none';
        opt.style.cursor = 'default';
    });
    
    // Apply feedback using CSS classes
    if (isCorrect) {
        // Add correct class for blood-drip animation
        options[answerIndex].classList.add('correct');
        currentQuiz.score++;
    } else {
        // Add incorrect class for red glow and shake
        options[answerIndex].classList.add('incorrect');
        
        // Also show the correct answer
        options[question.correct].classList.add('correct');
        
        // Play wrong sound (no mask overlay - removed as per requirements)
        const wrongAudio = document.getElementById('wrongSound');
        if (wrongAudio) {
            try { wrongAudio.currentTime = 0; wrongAudio.play().catch(() => {}); } catch (e) {}
        }
    }
    
    // Track answer
    const answerData = {
        question: question.question || question.q,
        selected: question.options ? question.options[answerIndex] : (question.a ? question.a[answerIndex] : ''),
        correct: isCorrect,
        isProfile: question.is_profile || false
    };
    currentQuiz.answers.push(answerData);
    
    // Track profile answer separately
    if (question.is_profile) {
        currentQuiz.profileAnswers.push(answerData.selected);
    }
    
    // Prefetch is now triggered when quiz starts, no need to trigger again here
    
    // Auto-advance after animation completes (1s for correct blood-drip, 1s for incorrect)
    currentQuiz.currentQuestion++;
    setTimeout(() => showQuestion(), 1000);
}

function showMaskOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'mask-overlay';
    const mask = document.createElement('div');
    mask.className = 'mask';
    overlay.appendChild(mask);
    document.body.appendChild(overlay);
    const splatter = document.createElement('div');
    splatter.className = 'blood-splatter';
    splatter.style.left = (10 + Math.random() * 80) + 'vw';
    splatter.style.top = (10 + Math.random() * 20) + 'vh';
    document.body.appendChild(splatter);
    document.body.classList.add('flicker');
    setTimeout(() => document.body.classList.remove('flicker'), 400);
    setTimeout(() => {
        if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        if (splatter.parentNode) splatter.parentNode.removeChild(splatter);
    }, 1300);
}

async function showQuizResults() {
    const quizContent = document.getElementById('quizContent');
    if (!quizContent) return;
    
    // Check if we're in Oracle mode - if so, submit to Oracle Engine
    if (oracleState.isOracleMode && currentQuiz.oracleData) {
        await submitToOracle();
        return;
    }
    
    let resultTitle = '';
    let resultMessage = '';
    
    switch(currentQuiz.score) {
        case 0:
            resultTitle = '💀 YOU DIED!';
            resultMessage = 'The killer got you in the first scene...';
            break;
        case 1:
            resultTitle = '🔪 YOU\'RE BLEEDING OUT!';
            resultMessage = 'Almost didn\'t make it to the sequel...';
            break;
        case 2:
            resultTitle = '🏃 YOU BARELY ESCAPED!';
            resultMessage = 'Close call... you\'ll have nightmares forever...';
            break;
        case 3:
            resultTitle = '🎭 YOU SURVIVED!';
            resultMessage = 'But you\'ll never be the same...';
            break;
        case 4:
            resultTitle = '👹 YOU\'RE THE FINAL GIRL/GUY!';
            resultMessage = 'Almost unstoppable!';
            break;
        case 5:
            resultTitle = '🩸 YOU\'RE THE KILLER!';
            resultMessage = 'Perfect horror knowledge... suspiciously perfect...';
            break;
    }
    
    // Save results locally first
    const quizHistory = JSON.parse(localStorage.getItem('horror-quiz-history') || '[]');
    const quizResult = {
        quizNumber: currentQuiz.quizNumber,
        score: currentQuiz.score,
        total: currentQuiz.questions.length,
        theme: currentQuiz.theme,
        difficulty: currentQuiz.difficulty,
        answers: currentQuiz.answers,
        timestamp: new Date().toISOString()
    };
    quizHistory.push(quizResult);
    localStorage.setItem('horror-quiz-history', JSON.stringify(quizHistory));
    
    // Update Horror DNA display
    loadHorrorDNADisplay();
    
    // Try to save to backend if user is logged in
    const savedUser = localStorage.getItem('horrorUser');
    let nextQuizMessage = '';
    
    if (savedUser) {
        try {
            const userObject = JSON.parse(savedUser);
            const response = await fetch(`${API_BASE}/save-quiz-results`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    googleId: userObject.sub,
                    quizResults: {
                        score: currentQuiz.score,
                        total: currentQuiz.questions.length,
                        theme: currentQuiz.theme,
                        answers: currentQuiz.answers,
                        profile_answers: currentQuiz.profileAnswers
                    }
                })
            });
            
            const data = await response.json();
            if (data.immersive_message) {
                nextQuizMessage = `<p class="text-sm text-red-300 mt-2 italic">${data.immersive_message}</p>`;
            }
        } catch (error) {
            console.error('Error saving quiz results:', error);
        }
    }
    
    quizContent.innerHTML = `
        <div class="text-center">
            <div class="mb-6">
                <h3 class="text-3xl font-bold text-red-500 mb-2" style="text-shadow: 0 0 15px rgba(255, 0, 0, 0.8);">
                    ${resultTitle}
                </h3>
                <p class="text-gray-300 text-lg mb-4">${resultMessage}</p>
                <div class="text-4xl font-bold text-yellow-400 mb-2">
                    ${currentQuiz.score}/${currentQuiz.questions.length}
                </div>
                <div class="text-sm text-gray-400 mb-2">
                    Theme: ${currentQuiz.theme} • ${currentQuiz.difficulty}
                </div>
                ${nextQuizMessage}
            </div>
            
            <div class="mb-6">
                <button onclick="startAdaptiveQuiz()" 
                        class="px-8 py-4 bg-gradient-to-r from-red-800 to-red-600 hover:from-red-700 hover:to-red-500 text-white rounded-full font-bold transition-all transform hover:scale-105 mb-4 shadow-lg border-2 border-red-400">
                    🧠 NEXT ADAPTIVE QUIZ
                </button>
                <br>
                <button onclick="closeBloodQuiz()" 
                        class="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-full font-bold transition-colors text-sm">
                    🎬 Back to Oracle
                </button>
            </div>
            
            <div class="border-t border-red-800 pt-4 mt-4">
                <p class="text-gray-500 text-xs mb-2">Your Horror DNA:</p>
                <div class="text-xs text-gray-400">
                    <span class="inline-block px-2 py-1 bg-red-950 rounded mr-2 mb-1">
                        Total Quizzes: ${quizHistory.length}
                    </span>
                    <span class="inline-block px-2 py-1 bg-red-950 rounded mr-2 mb-1">
                        Avg Score: ${(quizHistory.reduce((sum, q) => sum + (q.score / q.total), 0) / quizHistory.length * 100).toFixed(0)}%
                    </span>
                </div>
            </div>
        </div>
    `;
}

// ===== ORACLE ENGINE INTEGRATION =====

/**
 * Start Oracle quiz - calls the /api/start_quiz endpoint
 */
// ===== CINEMATIC SLIDESHOW PRELOAD SYSTEM =====

let preloadedQuizData = null; // Store preloaded quiz data
let slideshowInterval = null;
let currentSlideIndex = 0;

/**
 * Start the cinematic horror slideshow
 */
function startCinematicSlideshow() {
    console.log('🎬 Starting cinematic slideshow...');
    
    const slideshowOverlay = document.getElementById('introSlideshow');
    const slideshowImages = document.querySelectorAll('.slideshow-image');
    
    if (!slideshowOverlay || slideshowImages.length === 0) {
        console.error('❌ Slideshow elements not found!');
        return;
    }
    
    // Show the slideshow overlay
    slideshowOverlay.style.display = 'flex';
    slideshowOverlay.style.opacity = '1';
    setTimeout(() => {
        slideshowOverlay.classList.add('active');
    }, 50);
    
    currentSlideIndex = 0;
    slideshowImages[0].classList.add('active');
    
    // Cycle through images every 1.6 seconds (for 8 second total with 5 transitions)
    slideshowInterval = setInterval(() => {
        // Remove active from current image
        slideshowImages[currentSlideIndex].classList.remove('active');
        
        // Move to next image
        currentSlideIndex = (currentSlideIndex + 1) % slideshowImages.length;
        
        // Add active to next image
        slideshowImages[currentSlideIndex].classList.add('active');
        
        console.log(`🖼️ Slideshow: Image ${currentSlideIndex + 1}/${slideshowImages.length}`);
    }, 1600);
    
    // NOTE: Slideshow duration is now controlled by startSlideshowAndPreload()
    // Don't stop automatically here - let the parent function control the flow
}

/**
 * Stop the slideshow cycling
 */
function stopSlideshow() {
    if (slideshowInterval) {
        clearInterval(slideshowInterval);
        slideshowInterval = null;
        console.log('🎬 Slideshow complete');
    }
}

/**
 * REMOVED: Show the "Start Your Trials Now" button
 * This intermediate screen has been removed - slideshow now fades directly to Oracle Trial
 */

/**
 * Launch the quiz using preloaded data with fade-out effect
 */
async function launchPreloadedQuiz(quizData) {
    console.log('🚀 Launching preloaded quiz...');
    
    const slideshowOverlay = document.getElementById('introSlideshow');
    
    // Fade out the slideshow overlay
    if (slideshowOverlay) {
        slideshowOverlay.style.transition = 'opacity 0.5s ease-in-out';
        slideshowOverlay.style.opacity = '0';
        
        // Wait for fade to complete, then hide completely
        await new Promise(resolve => {
            setTimeout(() => {
                slideshowOverlay.style.display = 'none';
                slideshowOverlay.classList.remove('active');
                console.log('✅ Slideshow overlay hidden');
                resolve();
            }, 500);
        });
    }
    
    // Use the provided quiz data
    if (quizData) {
        console.log('✅ Using preloaded quiz data (instant load)');
        displayOracleQuizFromPreload(quizData);
    } else {
        console.error('❌ No quiz data provided to launchPreloadedQuiz!');
        alert('Failed to load quiz. Please try again.');
    }
}

/**
 * Preload quiz data in the background while slideshow runs
 */
async function preloadQuizData(userId, requestBody) {
    console.log('⏳ PRELOADING quiz data in background...');
    const preloadStartTime = performance.now();
    
    try {
        const response = await fetch(`${API_BASE}/api/start_quiz`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const quizData = await response.json();
        const preloadEndTime = performance.now();
        const preloadTime = ((preloadEndTime - preloadStartTime) / 1000).toFixed(2);
        
        console.log(`✅ PRELOAD COMPLETE in ${preloadTime}s`);
        console.log('✅ Preloaded Questions:', quizData.questions ? quizData.questions.length : 0);
        
        // Store preloaded data
        preloadedQuizData = quizData;
        
        return quizData;
    } catch (error) {
        console.error('❌ Preload failed:', error);
        
        // Retry once if failed
        console.log('🔄 Retrying preload...');
        try {
            const response = await fetch(`${API_BASE}/api/start_quiz`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            if (response.ok) {
                const quizData = await response.json();
                console.log('✅ Preload retry successful');
                preloadedQuizData = quizData;
                return quizData;
            }
        } catch (retryError) {
            console.error('❌ Preload retry also failed:', retryError);
        }
        
        return null;
    }
}

/**
 * Display quiz from preloaded data (instant, no loading)
 */
function displayOracleQuizFromPreload(quizData) {
    console.log('🎮 Displaying preloaded quiz...');
    
    // Store the Oracle quiz data
    currentQuiz.oracleData = quizData;
    
    // Set up current quiz state - MAP ORACLE QUESTIONS TO EXPECTED FORMAT
    if (quizData.questions && quizData.questions.length > 0) {
        currentQuiz.questions = quizData.questions.map((q, index) => {
            const options = q.choices || q.options || [];
            let correctIndex = 0; // Default to first option
            
            // Try multiple methods to find correct answer index
            if (typeof q.correct === 'number' && q.correct >= 0 && q.correct < options.length) {
                correctIndex = q.correct;
            } else if (q.correct_answer && Array.isArray(options)) {
                // Find by matching text (case-insensitive, trimmed)
                const target = String(q.correct_answer).trim().toLowerCase();
                const foundIndex = options.findIndex((opt) => 
                    String(opt).trim().toLowerCase() === target
                );
                if (foundIndex >= 0) {
                    correctIndex = foundIndex;
                } else if (q.choices && Array.isArray(q.choices)) {
                    // Fallback: try indexOf
                    const indexOfResult = q.choices.indexOf(q.correct_answer);
                    if (indexOfResult >= 0) {
                        correctIndex = indexOfResult;
                    }
                }
            } else if (typeof q.correct_index === 'number' && q.correct_index >= 0 && q.correct_index < options.length) {
                correctIndex = q.correct_index;
            }
            
            return {
                question: q.question || q.q || q.text || `Question ${index + 1}`,
                options: options,
                correct: correctIndex,
                is_profile: q.is_profile || false,
                theme: q.theme,
                difficulty: q.difficulty
            };
        });
        console.log('✅ Mapped questions to frontend format:', currentQuiz.questions.length, 'questions');
        console.log('✅ Sample question:', currentQuiz.questions[0]);
    } else {
        currentQuiz.questions = [];
        console.error('❌ No questions in preloaded data!');
        alert('⚠️ Quiz data failed to load. Please try again.');
        return;
    }
    
    // Validate we have questions
    if (!currentQuiz.questions || currentQuiz.questions.length === 0) {
        console.error('❌ CRITICAL: No questions after mapping!');
        alert('⚠️ Quiz failed to load questions. Please try again.');
        return;
    }
    
    currentQuiz.currentQuestion = 0;
    currentQuiz.score = 0;
    currentQuiz.answers = [];
    currentQuiz.quizNumber = (JSON.parse(localStorage.getItem('horror-quiz-history') || '[]').length + 1);
    currentQuiz.theme = quizData.theme || 'Horror Oracle';
    currentQuiz.difficulty = quizData.difficulty || 'intermediate';
    currentQuiz.profileAnswers = [];
    
    // Update fear level
    if (quizData.player_profile && quizData.player_profile.fear_level) {
        oracleState.fearLevel = quizData.player_profile.fear_level;
    }
    
    // Get the quiz modal and make it visible
    const modal = document.getElementById('quizModal');
    if (!modal) {
        console.error('❌ Quiz modal not found!');
        alert('Quiz modal element is missing from the page!');
        return;
    }
    
    // Make modal visible
    modal.style.display = 'flex';
    modal.classList.add('active');
    console.log('✅ Quiz modal made visible');
    
    // Get the quiz body container
    const quizBody = document.getElementById('quizBody');
    if (!quizBody) {
        console.error('❌ Quiz body container not found!');
        alert('Quiz body element is missing from the page!');
        return;
    }
    
    // Apply fear level styling
    applyFearLevelStyling(oracleState.fearLevel);
    
    // SKIP INTRO - Jump directly to first question!
    console.log('⚡ Jumping directly to first question (skipping intro)...');
    showQuestion();
    
    // Start prefetching next quiz immediately
    prefetchNextQuiz();
}

// ===== END CINEMATIC SLIDESHOW PRELOAD SYSTEM =====

// ===== PREFETCH NEXT QUIZ SYSTEM (SIMPLIFIED) =====
/**
 * Prefetch the next quiz in the background - simple and fast
 */
async function prefetchNextQuiz() {
    if (prefetchInProgress) return; // prevent duplicate calls
    prefetchInProgress = true;
    
    try {
        const res = await fetch(`${API_BASE}/api/start_quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: oracleState.userId,  // Fixed to match backend expectation
                difficulty: oracleState.nextDifficulty,
                theme: oracleState.nextTheme
            }),
            cache: 'no-cache'
        });
        
        nextQuizCache = await res.json();
        console.log('✅ Prefetched next quiz', nextQuizCache);
    } catch (err) {
        console.error('Prefetch failed:', err);
    } finally {
        prefetchInProgress = false;
    }
}

// ===== TRANSITION MANAGER FOR SMOOTH FADES =====
const transitionManager = {
    /**
     * Fast fade transition between content (≤300ms)
     */
    async fadeTransition(element, callback, duration = 300) {
        if (!element) return;
        
        // Fade out
        element.style.opacity = '1';
        element.style.transition = `opacity ${duration}ms ease`;
        element.style.opacity = '0';
        
        await new Promise(resolve => setTimeout(resolve, duration));
        
        // Execute callback (change content)
        if (callback) callback();
        
        // Fade in
        element.style.opacity = '1';
        
        await new Promise(resolve => setTimeout(resolve, duration));
    },
    
    /**
     * Instant content swap with brief fade
     */
    async quickSwap(element, newContent, duration = 200) {
        if (!element) return;
        
        element.style.transition = `opacity ${duration}ms ease`;
        element.style.opacity = '0';
        
        await new Promise(resolve => setTimeout(resolve, duration));
        
        element.innerHTML = newContent;
        element.style.opacity = '1';
    }
};

/**
 * Continue to next quiz using cached data (instant transition)
 */
async function continueToNextQuiz() {
    const quizBody = document.getElementById('quizBody');
    if (!quizBody) return;
    
    // Show quick loading
    await transitionManager.quickSwap(quizBody, `
        <div style="text-align: center; padding: 2rem;">
            <div style="color: #ff0000; font-size: 2rem; margin-bottom: 1rem; animation: pulse 1s infinite;">⚡</div>
            <div style="color: #ccc;">Entering next chamber...</div>
        </div>
    `, 200);
    
    try {
        let quizData;
        
        // Use cached quiz if available, otherwise fetch using cached endpoint first
        if (nextQuizCache) {
            console.log('🚀 Using cached quiz - INSTANT');
            quizData = nextQuizCache;
            nextQuizCache = null; // clear cache for next cycle
        } else {
            console.log('⚠️ Cache empty, attempting /api/get_cached_quiz');
            try {
                const cachedRes = await fetch(`${API_BASE}/api/get_cached_quiz`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                    cache: 'no-cache'
                });
                if (cachedRes.ok) {
                    quizData = await cachedRes.json();
                } else {
                    throw new Error(`Cached fetch failed: ${cachedRes.status}`);
                }
            } catch (cachedErr) {
                console.warn('⚠️ /api/get_cached_quiz failed, falling back to live generation', cachedErr);
                const res = await fetch(`${API_BASE}/api/start_quiz`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: oracleState.userId,  // Fixed to match backend expectation
                        difficulty: oracleState.nextDifficulty,
                        theme: oracleState.nextTheme
                    })
                });
                quizData = await res.json();
            }
        }
        
        // Set current quiz state
        currentQuiz.oracleData = quizData;
        currentQuiz.questions = quizData.questions || [];
        currentQuiz.currentQuestion = 0;
        currentQuiz.answers = [];
        currentQuiz.theme = quizData.theme || 'Horror Oracle';
        currentQuiz.difficulty = quizData.difficulty || 'Unknown';
        
        // Update fear level
        if (quizData.player_profile && quizData.player_profile.fear_level) {
            oracleState.fearLevel = quizData.player_profile.fear_level;
        }
        
        // Display the new quiz intro
        displayOracleQuiz(quizData);
        
        // Start prefetching next one
        prefetchNextQuiz();
        
        console.log('✅ Next quiz loaded!');
        
    } catch (error) {
        console.error('❌ Error loading next quiz:', error);
        showErrorMessage('Failed to load next quiz. Please try again.');
    }
}

// ===== END PREFETCH SYSTEM =====

async function startOracleQuiz() {
    console.log('🔮 Starting Oracle Quiz with Cinematic Preload...');
    
    // Find and disable the Face Your Nightmares button to prevent double-clicking
    const nightmareBtn = document.getElementById('nightmare-quiz-btn');
    if (nightmareBtn) {
        nightmareBtn.disabled = true;
        nightmareBtn.classList.add('clicked');
        console.log('[DEBUG] 🟢 Face Your Nightmares button disabled and marked as clicked');
    }
    
    // Get user ID from localStorage or use guest
    const savedUser = localStorage.getItem('horrorUser');
    let userId = 'guest';
    if (savedUser) {
        try {
            const userObject = JSON.parse(savedUser);
            userId = userObject.sub || userObject.email || 'guest';
        } catch (e) {
            console.error('Error parsing user:', e);
        }
    }
    
    oracleState.userId = userId;
    oracleState.isOracleMode = true;
    
    // Build request body with optional difficulty and theme overrides
    // FIXED: Use 'user_id' to match backend API expectation
    const requestBody = { 
        user_id: userId,
        force_new: true  // Force new question generation
    };
    
    // Use stored next difficulty and theme from previous quiz if available
    if (oracleState.nextDifficulty) {
        requestBody.difficulty = oracleState.nextDifficulty;
        console.log(`🎯 Using recommended difficulty: ${oracleState.nextDifficulty}`);
    }
    if (oracleState.nextTheme) {
        requestBody.theme = oracleState.nextTheme;
        console.log(`🎨 Using recommended theme: ${oracleState.nextTheme}`);
    }
    
    // ===== CINEMATIC PRELOAD: Perfect Flow =====
    // [Face Your Nightmares] → Slideshow (8s) → Fade → Quiz screen
    await startSlideshowAndPreload(userId, requestBody, nightmareBtn);
}

/**
 * OPTIMIZED: Parallel loading with Promise.all - slideshow + quiz fetch simultaneously
 */
async function startSlideshowAndPreload(userId, requestBody, nightmareBtn) {
    try {
        console.log('🎬🔮 Starting PARALLEL slideshow + quiz load...');
        
        // 1. Start slideshow immediately
        startCinematicSlideshow();
        
        // 2. Define both operations to run in parallel
        const slideshowDuration = 3000; // Reduced from 8s to 3s for faster UX
        const slideshowPromise = new Promise(resolve => setTimeout(resolve, slideshowDuration));
        
        // UPDATED: Use unified startQuiz() function instead of direct fetch
        const quizPromise = startQuiz(userId, null).then(quizData => {
            // Validate quizData before accessing properties
            if (!quizData) {
                throw new Error('Quiz data is undefined');
            }
            
            // Transform to format expected by displayOracleQuiz
            return {
                ...(quizData.oracleData || {}),
                questions: (quizData.questions || []).map(q => ({
                    question: q.question,
                    choices: q.options,
                    correct_answer: q.options[q.correct],
                    is_profile: q.is_profile || false
                }))
            };
        });
        
        // 3. Run BOTH in parallel using Promise.all
        console.log('⚡ Running slideshow (3s) + quiz fetch in PARALLEL...');
        const [_, quizData] = await Promise.all([slideshowPromise, quizPromise]);
        console.log('✅ Both slideshow and quiz data ready!');
        
        // CRITICAL FIX: Validate quiz data before proceeding
        if (!quizData || !quizData.questions || quizData.questions.length === 0) {
            throw new Error('Invalid quiz data received from server');
        }
        console.log('✅ Quiz data validated:', quizData.questions.length, 'questions');
        
        // 4. Stop slideshow animation
        stopSlideshow();
        
        // 5. Fade out slideshow and load quiz screen instantly
        await launchPreloadedQuiz(quizData);
        
        console.log('✅ FAST transition complete: Slideshow → Quiz (parallel load)');
        
    } catch (error) {
        console.error('❌ Error during slideshow preload:', error);
        
        // Stop slideshow
        stopSlideshow();
        
        // Force hide slideshow overlay immediately
        const slideshowOverlay = document.getElementById('introSlideshow');
        if (slideshowOverlay) {
            slideshowOverlay.style.transition = 'none';
            slideshowOverlay.style.display = 'none';
            slideshowOverlay.style.opacity = '0';
            slideshowOverlay.classList.remove('active');
        }
        
        // Re-enable button on error
        if (nightmareBtn) {
            nightmareBtn.disabled = false;
            nightmareBtn.classList.remove('clicked');
        }
        
        alert('Failed to load quiz: ' + error.message + '\n\nPlease make sure the server is running and try again.');
    }
}

/**
 * Display Oracle quiz with atmospheric intro
 */
function displayOracleQuiz(quizData) {
    console.log('🎮 displayOracleQuiz called with data:', quizData);
    
    // Get the quiz modal from HTML
    const modal = document.getElementById('quizModal');
    if (!modal) {
        console.error('❌ Quiz modal not found!');
        alert('Quiz modal element is missing from the page!');
        return;
    }
    
    // CRITICAL FIX: Ensure modal is visible before doing anything else
    modal.style.display = 'flex';
    modal.classList.add('active');
    console.log('✅ Quiz modal made visible');
    
    // Get the quiz body container from HTML
    const quizBody = document.getElementById('quizBody');
    if (!quizBody) {
        console.error('❌ Quiz body container not found!');
        alert('Quiz body element is missing from the page!');
        return;
    }
    
    // Show bloody dagger loading animation
    showBloodyDaggerLoading();
    console.log('🔪 Loading animation started');
    
    // Clear old question HTML completely after a brief delay
    setTimeout(() => {
        quizBody.innerHTML = '';
        console.log('🧹 Cleared old quiz HTML');
        
        // Hide loading, show fear level
        hideBloodyDaggerLoading();
        console.log('✅ Loading animation stopped');
        
        // Normalize and set current quiz data BEFORE showing intro
        (function() {
            function normalizeQuizQuestions(questions) {
                if (!Array.isArray(questions)) return [];
                return questions.map((q) => {
                    const questionText = q.question || q.q || q.text || '';
                    const options = q.options || q.a || q.choices || [];
                    let correctIndex = typeof q.correct === 'number' ? q.correct : (
                        typeof q.correct_index === 'number' ? q.correct_index : -1
                    );
                    if (correctIndex === -1 && q.correct_answer && Array.isArray(options)) {
                        const target = String(q.correct_answer).trim().toLowerCase();
                        correctIndex = options.findIndex((opt) => String(opt).trim().toLowerCase() === target);
                    }
                    return {
                        question: questionText,
                        options: options,
                        correct: correctIndex,
                        is_profile: q.is_profile || false
                    };
                });
            }
            // Update currentQuiz state for the upcoming session
            currentQuiz.questions = normalizeQuizQuestions(quizData.questions || []);
            currentQuiz.currentQuestion = 0;
            currentQuiz.score = 0;
            currentQuiz.quizNumber = (JSON.parse(localStorage.getItem('horror-quiz-history') || '[]').length + 1);
            currentQuiz.theme = quizData.theme || 'Horror Oracle';
            currentQuiz.difficulty = quizData.difficulty || 'intermediate';
            currentQuiz.answers = [];
            currentQuiz.profileAnswers = [];
            currentQuiz.oracleData = quizData;
            console.log('✅ currentQuiz initialized for next session:', currentQuiz);
        })();

        // Show Oracle's intro with lore
        const intro = quizData.intro || 'The Oracle awaits your challenge...';
        const room = quizData.room || 'The First Chamber';
        const lore = quizData.lore || {};
        
        // Log unique chamber for debugging and verification
        console.log('✅ Next quiz loaded');
        console.log(`🎃 New Chamber: ${room}`);
        console.log(`📋 Quiz Theme: ${quizData.theme || 'general_horror'}`);
        console.log(`⚡ Difficulty: ${quizData.difficulty || 'intermediate'}`);
        console.log(`🔮 Tone: ${quizData.tone || 'creepy'}`);
        
        // Smooth fade transition
        quizBody.style.opacity = '0';
        setTimeout(() => {
            quizBody.style.transition = 'opacity 0.5s ease-in-out';
            quizBody.style.opacity = '1';
        }, 50);
        
        quizBody.innerHTML = `
        <div class="oracle-intro-container">
            <h1 class="oracle-main-title" id="oracleMainTitle">THE ORACLE'S TRIAL</h1>
            <div class="oracle-room-title">
                ${room}
            </div>
            <div class="oracle-intro-text">
                ${intro}
            </div>
            ${lore.whisper ? `
                <div class="oracle-lore-whisper" style="color: #999; font-style: italic; font-size: 0.95rem; margin: 1rem 0 2rem; border-left: 3px solid #b91c1c; padding-left: 1rem; max-width: 700px;">
                    ${lore.whisper}
                </div>
            ` : ''}
            <button onclick="startOracleQuestion()" class="oracle-begin-btn">
                ENTER NIGHTMARE
            </button>
        </div>
        `;
        
        // Start blood drip animation after a short delay
        setTimeout(() => {
            spawnBloodDrips();
            // Continue spawning drips periodically
            const dripInterval = setInterval(spawnBloodDrips, 3000);
            // Store interval ID to clear it later if needed
            window.oracleDripInterval = dripInterval;
        }, 500);
        
        // Apply initial fear level styling
        applyFearLevelStyling(oracleState.fearLevel);
    }, 500); // FIXED: Reduced from 3000ms to 500ms - much faster loading!
}

/**
 * Helper functions for bloody dagger loading animation
 */
function showBloodyDaggerLoading() {
    // Hide progress bar and fear level display
    const progressBar = document.getElementById('quizProgressBar');
    const fearDisplay = document.getElementById('fearLevelDisplay');
    const daggerLoader = document.getElementById('bloodyDaggerLoader');
    
    if (progressBar) progressBar.style.display = 'none';
    if (fearDisplay) fearDisplay.style.display = 'none';
    if (daggerLoader) {
        daggerLoader.style.display = 'block';
    }
}

function hideBloodyDaggerLoading() {
    // Show fear level, hide loading dagger
    const daggerLoader = document.getElementById('bloodyDaggerLoader');
    const fearDisplay = document.getElementById('fearLevelDisplay');
    const progressBar = document.getElementById('quizProgressBar');
    
    if (daggerLoader) daggerLoader.style.display = 'none';
    if (fearDisplay) {
        fearDisplay.style.display = 'flex';
        // Set random fear level
        const fearLevel = Math.floor(Math.random() * 100) + 1;
        const fearText = document.getElementById('fearLevelText');
        if (fearText) fearText.textContent = `Fear Level: ${fearLevel}`;
    }
    if (progressBar) progressBar.style.display = 'flex';
}

/**
 * Show Oracle Speaks section with reaction text
 */
function showOracleSpeaks(reactionText) {
    const oracleSection = document.getElementById('oracleSpeaksSection');
    const oracleText = document.getElementById('oracleSpeaksText');
    
    if (oracleSection && oracleText) {
        oracleText.textContent = reactionText;
        oracleSection.style.display = 'block';
        oracleSection.style.animation = 'oracleFadeIn 0.8s ease-out';
        
        // Auto-hide after 4 seconds
        setTimeout(() => {
            oracleSection.style.animation = 'oracleFadeIn 0.5s ease-out reverse';
            setTimeout(() => {
                oracleSection.style.display = 'none';
            }, 500);
        }, 4000);
    }
}

/**
 * Start showing Oracle questions
 */
function startOracleQuestion() {
    console.log('[DEBUG] ▶️ startOracleQuestion called');
    console.log('[DEBUG] currentQuiz object:', currentQuiz);
    console.log('[DEBUG] currentQuiz.questions:', currentQuiz.questions);
    console.log('[DEBUG] Number of questions:', currentQuiz.questions ? currentQuiz.questions.length : 0);
    
    // Find and disable the BEGIN THE TRIAL button to prevent double-clicking
    const beginBtn = document.querySelector('.oracle-begin-btn');
    if (beginBtn) {
        beginBtn.disabled = true;
        beginBtn.classList.add('clicked');
        console.log('[DEBUG] 🟢 Button disabled and marked as clicked');
    }
    
    // Check if we have questions loaded
    if (!currentQuiz.questions || currentQuiz.questions.length === 0) {
        console.error('❌ ERROR: No questions loaded in currentQuiz!');
        console.error('❌ currentQuiz.oracleData:', currentQuiz.oracleData);
        
        // Try to recover if we have oracleData
        if (currentQuiz.oracleData && currentQuiz.oracleData.questions) {
            console.log('🔄 Attempting to recover questions from oracleData...');
            currentQuiz.questions = currentQuiz.oracleData.questions.map(q => ({
                question: q.question,
                options: q.choices || q.options || [],
                correct: q.choices ? q.choices.indexOf(q.correct_answer) : 0,
                is_profile: q.is_profile || false
            }));
            console.log('✅ Recovered questions:', currentQuiz.questions);
        } else {
            alert('⚠️ Quiz data failed to load. Please close and try again.');
            // Re-enable button on error
            if (beginBtn) {
                beginBtn.disabled = false;
                beginBtn.classList.remove('clicked');
            }
            return;
        }
    }
    
    console.log('[DEBUG] ✅ Starting quiz with', currentQuiz.questions.length, 'questions');
    showQuestion();
    
    // Start prefetching next quiz immediately when first quiz starts
    prefetchNextQuiz();
    
    // Button will stay in clicked state until the question is displayed
    // The showQuestion() function will handle the UI transition
}

/**
 * ===== UNIFIED QUIZ SUBMISSION FUNCTION =====
 * This function replaces all old static result calculations.
 * It ALWAYS submits to /api/submit_answers and receives dynamic LangChain-generated results.
 * 
 * DATA FLOW: Frontend → POST /api/submit_answers → LangChain Evaluator → Returns { score, reward, reaction, next_difficulty, profile, recommendations }
 * 
 * @param {Object} answers - User's answers (can be currentQuiz.answers array or answersDict object)
 * @returns {Promise<Object>} Evaluation result with score, rewards, Oracle reaction, recommendations, etc.
 */
async function submitAnswers(answers = null) {
    console.log('[LANGCHAIN QUIZ] 🔮 Submitting answers to /api/submit_answers endpoint');
    
    try {
        // Use provided answers or currentQuiz.answers
        let answersDict = {};
        
        if (answers && typeof answers === 'object' && !Array.isArray(answers)) {
            // Already in dict format
            answersDict = answers;
        } else {
            // Convert currentQuiz.answers array to dict format expected by backend
            const answersArray = answers || currentQuiz.answers || [];
            answersArray.forEach((answer, index) => {
                answersDict[`q${index}`] = answer.selected || answer.answer || answer;
            });
        }
        
        // Get user ID
        const userId = oracleState.userId || (() => {
            const savedUser = localStorage.getItem('horrorUser');
            if (savedUser) {
                try {
                    const userObject = JSON.parse(savedUser);
                    return userObject.sub || userObject.email || 'guest';
                } catch (e) {
                    return 'guest';
                }
            }
            return 'guest';
        })();
        
        // Submit to Flask backend → LangChain Evaluator
        const response = await fetch(`${API_BASE}/api/submit_answers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                quiz: currentQuiz.oracleData || {},  // Full quiz data from Oracle Engine
                answers: answersDict
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('[LANGCHAIN QUIZ] ✅ Evaluation Result received from LangChain');
        console.log('[LANGCHAIN QUIZ] 📊 Score:', result.score, '/', result.out_of, `(${result.percentage}%)`);
        
        // Update Oracle state with LangChain-generated data
        if (result.player_profile && result.player_profile.fear_level !== undefined) {
            oracleState.fearLevel = result.player_profile.fear_level;
            console.log(`[LANGCHAIN QUIZ] 🎭 Fear Level updated: ${oracleState.fearLevel}`);
        }
        
        // Store next difficulty and theme for adaptive progression
        if (result.next_difficulty) {
            oracleState.nextDifficulty = result.next_difficulty;
            console.log(`[LANGCHAIN QUIZ] 🎯 Next Difficulty: ${result.next_difficulty}`);
        }
        if (result.next_theme) {
            oracleState.nextTheme = result.next_theme;
            console.log(`[LANGCHAIN QUIZ] 🎨 Next Theme: ${result.next_theme}`);
        }
        
        // Update currentQuiz with results
        if (result.score !== undefined) {
            currentQuiz.score = result.score;
        }
        
        // Return result for caller to handle display
        return result;
        
    } catch (error) {
        console.error('[LANGCHAIN QUIZ] ❌ Error submitting answers:', error);
        throw error;
    }
}

/**
 * ===== LEGACY WRAPPER: submitToOracle() =====
 * This function wraps submitAnswers() for backward compatibility.
 * It automatically displays results after submission.
 */
async function submitToOracle() {
    try {
        const result = await submitAnswers();
        
        // Display Oracle's reaction and rewards
        displayOracleResults(result);
        
        // Start prefetching next quiz while user reads results
        prefetchNextQuiz();
        
    } catch (error) {
        showErrorMessage('Failed to submit to the Oracle. Please try again.');
    }
}

/**
 * Display Oracle's reaction, rewards, and updated fear level
 */
function displayOracleResults(result) {
    const quizBody = document.getElementById('quizBody');
    if (!quizBody) return;
    
    // Extract data from result
    const score = result.score || 0;
    const total = result.out_of || currentQuiz.questions.length;
    const percentage = result.percentage || 0;
    const evaluation = result.evaluation || {};
    const oracleReaction = evaluation.oracle_reaction || 'The Oracle observes in silence...';
    const oracleStateData = result.oracle_state || {};
    const rewards = result.rewards || {};
    const lore = result.lore || {};
    const fearLevel = oracleState.fearLevel;
    
    // Apply fear level styling with animation
    applyFearLevelStyling(fearLevel);
    
    // Build rewards HTML
    let rewardsHTML = '';
    if (rewards.reward_name) {
        rewardsHTML = `
            <div class="oracle-reward-popup" style="background: rgba(139, 0, 0, 0.3); border: 2px solid #fbbf24; border-radius: 8px; padding: 1.5rem; margin: 1.5rem 0; animation: rewardFadeIn 1.5s ease;">
                <div style="color: #fbbf24; font-weight: bold; font-size: 1.2rem; margin-bottom: 0.5rem;">
                    ✨ ${rewards.reward_name} ✨
                </div>
                <div style="color: #ccc; font-size: 0.95rem;">
                    ${rewards.reward_description || 'A dark gift from the Oracle...'}
                </div>
                ${rewards.lore_fragment ? `
                    <div style="color: #999; font-style: italic; font-size: 0.85rem; margin-top: 0.5rem; border-top: 1px solid #555; padding-top: 0.5rem;">
                        ${rewards.lore_fragment}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Build lore HTML
    let loreHTML = '';
    if (lore.whisper) {
        loreHTML = `
            <div class="oracle-lore-whisper" style="color: #999; font-style: italic; font-size: 0.95rem; margin: 1.5rem 0; border-left: 3px solid #b91c1c; padding-left: 1rem; text-align: left;">
                "${lore.whisper}"
            </div>
        `;
    }
    
    // Build recommendations HTML from LangChain Recommender Node
    let recommendationsHTML = '';
    const recommendations = result.recommendations || [];
    if (recommendations.length > 0) {
        recommendationsHTML = `
            <div id="oracle-recommendations" style="margin: 2rem 0; padding: 1.5rem; background: rgba(139, 0, 0, 0.2); border: 2px solid #b91c1c; border-radius: 8px;">
                <div style="color: #b91c1c; font-weight: bold; font-size: 1.1rem; margin-bottom: 1rem;">
                    🎬 THE ORACLE RECOMMENDS:
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    ${recommendations.slice(0, 6).map(rec => `
                        <div style="text-align: center; background: rgba(0, 0, 0, 0.5); padding: 0.75rem; border-radius: 6px; border: 1px solid #555;">
                            ${rec.poster ? `
                                <img src="${rec.poster}" 
                                     alt="${rec.title || rec.name || 'Movie'}" 
                                     style="width: 100%; height: auto; border-radius: 4px; margin-bottom: 0.5rem;"
                                     onerror="this.style.display='none'">
                            ` : ''}
                            <div style="color: #ccc; font-size: 0.85rem; font-weight: bold;">
                                ${rec.title || rec.name || 'Movie'}
                            </div>
                            ${rec.year ? `<div style="color: #999; font-size: 0.75rem;">${rec.year}</div>` : ''}
                            ${rec.reason ? `<div style="color: #999; font-size: 0.7rem; font-style: italic; margin-top: 0.25rem;">${rec.reason}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    quizBody.innerHTML = `
        <div class="oracle-results-container" style="text-align: center; padding: 2rem;">
            <div class="oracle-score" style="font-size: 3rem; font-weight: bold; color: #ff0000; text-shadow: 0 0 20px #ff0000; margin-bottom: 1rem;">
                ${score}/${total}
            </div>
            <div style="color: #ccc; font-size: 1.2rem; margin-bottom: 1rem;">
                ${percentage}% Correct
            </div>
            
            <div id="oracle-reaction" class="oracle-reaction-box" style="min-height: 100px; background: rgba(139, 0, 0, 0.2); border: 2px solid #b91c1c; border-radius: 8px; padding: 1.5rem; margin: 2rem 0; opacity: 0; animation: oracleFadeIn 2s ease forwards;">
                <div style="color: #b91c1c; font-weight: bold; margin-bottom: 1rem; font-size: 1.1rem;">
                    THE ORACLE SPEAKS:
                </div>
                <div class="oracle-reaction-text" style="color: #e0e0e0; font-size: 1rem; line-height: 1.6;">
                    ${oracleReaction}
                </div>
                ${oracleStateData.atmospheric_message ? `
                    <div style="color: #999; font-style: italic; font-size: 0.9rem; margin-top: 1rem; border-top: 1px solid #555; padding-top: 1rem;">
                        ${oracleStateData.atmospheric_message}
                    </div>
                ` : ''}
            </div>
            
            ${rewardsHTML}
            ${loreHTML}
            ${recommendationsHTML}
            
            <div id="fear-meter" class="fear-meter-container" style="margin: 2rem 0;">
                <div style="color: #b91c1c; font-weight: bold; margin-bottom: 0.5rem;">FEAR LEVEL</div>
                <div class="fear-meter-bar" style="width: 100%; height: 30px; background: #1a1a1a; border: 2px solid #b91c1c; border-radius: 15px; overflow: hidden; position: relative;">
                    <div class="fear-meter-fill" style="height: 100%; background: linear-gradient(90deg, #ff0000, #8b0000); width: ${fearLevel}%; transition: width 1s ease;">
                    </div>
                    <div class="fear-meter-text" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: bold; text-shadow: 0 0 5px #000;">
                        ${fearLevel}%
                    </div>
                </div>
            </div>
            
            <div id="nextChamberSection" style="margin-top: 2rem; opacity: 0; animation: oracleFadeIn 1s ease 2s forwards;">
                <p style="color: #999; font-size: 0.9rem; margin-bottom: 1rem;">
                    The Oracle prepares the next chamber...
                </p>
                <button onclick="closeBloodQuiz()" style="padding: 1rem 2rem; background: #333; color: white; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: all 0.3s;">
                    🎬 Return to Oracle
                </button>
            </div>
        </div>
    `;
    
    // OPTIMIZED: Instant transition using prefetched quiz
    // Show "Continue" button that uses cached data
    setTimeout(() => {
        const nextChamberSection = document.getElementById('nextChamberSection');
        if (nextChamberSection) {
            nextChamberSection.innerHTML = `
                <p style="color: #999; font-size: 0.9rem; margin-bottom: 1rem;">
                    ${nextQuizCache ? '⚡ Next chamber is ready!' : '⏳ Preparing next chamber...'}
                </p>
                <button onclick="continueToNextQuiz()" style="padding: 1rem 2rem; background: linear-gradient(135deg, #b91c1c, #7d0b0b); color: white; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: all 0.3s; box-shadow: 0 0 20px rgba(185, 28, 28, 0.5);">
                    ${nextQuizCache ? '▶️ CONTINUE TRIAL' : '⏳ Loading...'}
                </button>
            `;
        }
    }, 2000);
}

/**
 * Apply visual styling based on fear level
 */
function applyFearLevelStyling(fearLevel) {
    const body = document.body;
    
    // Remove existing fear classes
    body.classList.remove('fear-low', 'fear-medium', 'fear-high', 'fear-extreme');
    
    // Apply appropriate class based on fear level
    if (fearLevel <= 30) {
        body.classList.add('fear-low');
    } else if (fearLevel <= 60) {
        body.classList.add('fear-medium');
    } else if (fearLevel <= 85) {
        body.classList.add('fear-high');
    } else {
        body.classList.add('fear-extreme');
    }
    
    console.log(`🎭 Fear Level: ${fearLevel} - Applied styling`);
}

/**
 * Show error message in quiz modal
 */
function showErrorMessage(message) {
    const quizBody = document.getElementById('quizBody');
    if (!quizBody) return;
    
    quizBody.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div style="color: #ff0000; font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
            <div style="color: #ccc; font-size: 1.2rem; margin-bottom: 2rem;">
                ${message}
            </div>
            <button onclick="closeBloodQuiz()" style="padding: 1rem 2rem; background: #333; color: white; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: bold; cursor: pointer;">
                Close
            </button>
        </div>
    `;
}

// ===== END ORACLE ENGINE INTEGRATION =====

/**
 * Close the quiz modal (for Oracle quiz)
 */
function closeQuiz() {
    const modal = document.getElementById('quizModal');
    if (modal) {
        modal.classList.remove('active');
    }
    
    // Reset Oracle state
    oracleState.isOracleMode = false;
    
    // Reset quiz state
    currentQuiz = {
        questions: [],
        currentQuestion: 0,
        score: 0,
        category: 'general',
        quizNumber: 1,
        theme: '',
        difficulty: '',
        answers: [],
        profileAnswers: [],
        oracleData: null
    };
}

function addToMyList(movieTitle) {
    let myList = JSON.parse(localStorage.getItem('horror-my-list') || '[]');
    
    if (!myList.includes(movieTitle)) {
        myList.push(movieTitle);
        localStorage.setItem('horror-my-list', JSON.stringify(myList));
        loadMyList();
        
        // Show confirmation
        showToast(`Added "${movieTitle}" to My List!`);
    } else {
        showToast(`"${movieTitle}" is already in your list!`);
    }
}

function loadMyList() {
    const myList = JSON.parse(localStorage.getItem('horror-my-list') || '[]');
    
    if (myList.length === 0) {
        myListContainer.innerHTML = '<li class="text-center text-gray-400 text-xs">Empty</li>';
    } else {
        myListContainer.innerHTML = myList.map(movie => 
            `<li class="text-gray-300 text-xs cursor-pointer hover:text-red-400 transition-colors" 
                 onclick="searchMovie('${movie}')">${movie}</li>`
        ).join('');
    }
}

function searchMovie(movieTitle) {
    userInput.value = movieTitle;
    sendMessage();
}

// ===== MOVIE SECTIONS UPDATES =====
function updateStreamingSection(movieDetails) {
    if (!movieDetails) return;
    
    const streamingHtml = `
        <div class="bg-gray-800 rounded-lg p-3 border border-gray-600">
            <div class="flex items-center space-x-3">
                ${movieDetails.poster ? 
                    `<img src="${movieDetails.poster}" 
                         alt="${movieDetails.title}" 
                         class="streaming-movie-poster"
                         onerror="this.src='https://via.placeholder.com/50x75/000000/FF0000?text=No+Poster'">` 
                    : ''}
                <div class="flex-1">
                    <h3 class="movie-title-streaming">${movieDetails.title}</h3>
                    ${movieDetails.year ? `<p class="text-gray-400 text-xs">${movieDetails.year}</p>` : ''}
                    
                    <div class="flex flex-wrap gap-1 mt-2">
                        <span class="streaming-tag streaming-netflix">Netflix</span>
                        <span class="streaming-tag streaming-prime">Prime Video</span>
                        <span class="streaming-tag streaming-shudder">Shudder</span>
                    </div>
                    
                    <button onclick="suggestSimilar('${movieDetails.title}')" 
                            class="w-full mt-2 px-2 py-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 transition-colors">
                        🎬 Similar Movies
                    </button>
                </div>
            </div>
        </div>
    `;
    
    streamingContainer.innerHTML = streamingHtml;
}

function updateMovieSections(movieDetails, recommendations) {
    if (movieDetails) {
        updateStreamingSection(movieDetails);
    }
    if (recommendations) {
        updateRecommendations(recommendations);
    }
}

function updateRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        recommendationsContainer.innerHTML = '<div class="text-center p-2"><p class="text-gray-400 text-xs">No recommendations available</p></div>';
        return;
    }
    
    const recsHtml = recommendations.map(rec => `
        <div class="rec-card p-2 cursor-pointer" onclick="searchMovie('${rec.title}')">
            <div class="flex items-center space-x-2">
                ${rec.poster ? 
                    `<img src="${rec.poster}" 
                         alt="${rec.title}" 
                         class="w-12 h-18 object-cover rounded border border-gray-600"
                         onerror="this.src='https://via.placeholder.com/48x72/000000/FF0000?text=No+Poster'">` 
                    : ''}
                <div class="flex-1 min-w-0">
                    <h4 class="text-white text-xs font-semibold truncate">${rec.title}</h4>
                    ${rec.year ? `<p class="text-gray-400 text-xs">${rec.year}</p>` : ''}
                </div>
            </div>
        </div>
    `).join('');
    
    recommendationsContainer.innerHTML = recsHtml;
}

// ===== RATING SYSTEM =====
function setupRatingSystem() {
    const stars = document.querySelectorAll('.star');
    
    stars.forEach((star, index) => {
        const rating = index + 1;
        
        star.addEventListener('mouseenter', function() {
            highlightStars(rating, 'hover');
        });
        
        star.addEventListener('mouseleave', function() {
            clearStarHighlight();
            if (userRating > 0) {
                highlightStars(userRating, 'filled');
            }
        });
        
        star.addEventListener('click', function() {
            userRating = rating;
            highlightStars(rating, 'filled');
            submitRating(rating);
        });
    });
}

function highlightStars(rating, className) {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        star.classList.remove('filled', 'hover');
        if (index < rating) {
            star.classList.add(className);
            star.textContent = '★';
        } else {
            star.textContent = '☆';
        }
    });
}

function clearStarHighlight() {
    const stars = document.querySelectorAll('.star');
    stars.forEach(star => {
        star.classList.remove('hover');
    });
}

async function submitRating(rating) {
    if (!currentMovie) {
        showToast('Please search for a movie first!');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/submit-rating`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                movie_title: currentMovie,
                rating: rating
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showToast(`Error: ${data.error}`);
        } else {
            showToast('Rating submitted!');
            // Refresh movie stats
            loadMovieStats(currentMovie);
        }
    } catch (error) {
        console.error('Rating submission error:', error);
        showToast('Failed to submit rating');
    }
}

async function submitReview() {
    const reviewInput = document.getElementById('review-input');
    const reviewText = reviewInput.value.trim();
    
    if (!reviewText) {
        showToast('Please enter a review!');
        return;
    }
    
    if (!currentMovie) {
        showToast('Please search for a movie first!');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/submit-review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                movie_title: currentMovie,
                review: reviewText
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showToast(`Error: ${data.error}`);
        } else {
            showToast('Review submitted!');
            reviewInput.value = '';
            // Refresh movie stats
            loadMovieStats(currentMovie);
        }
    } catch (error) {
        console.error('Review submission error:', error);
        showToast('Failed to submit review');
    }
}

// ===== MOVIE STATS =====
async function loadMovieStats(movieTitle) {
    if (!movieTitle) return;
    
    try {
        const response = await fetch(`${API_BASE}/get-movie-stats?movie_title=${encodeURIComponent(movieTitle)}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('Stats error:', data.error);
            return;
        }
        
        currentMovieStats = data;
        updateStatsDisplay(movieTitle, data);
    } catch (error) {
        console.error('Error loading movie stats:', error);
    }
}

function updateStatsDisplay(movieTitle, stats) {
    // Show the stats section
    const currentMovieDisplay = document.getElementById('current-movie-display');
    const noMovieSelected = document.getElementById('no-movie-selected');
    
    if (currentMovieDisplay && noMovieSelected) {
        currentMovieDisplay.classList.remove('hidden');
        noMovieSelected.classList.add('hidden');
        
        // Update movie title
        const statsMovieTitle = document.getElementById('stats-movie-title');
        if (statsMovieTitle) {
            statsMovieTitle.textContent = movieTitle;
        }
        
        // Update community rating
        const communityStars = document.getElementById('community-stars');
        const ratingValue = document.getElementById('rating-value');
        const ratingCount = document.getElementById('rating-count');
        
        if (communityStars && ratingValue && ratingCount) {
            const rating = stats.rating.average;
            const filledStars = Math.floor(rating);
            const halfStar = rating % 1 >= 0.5;
            
            let starsHtml = '';
            for (let i = 0; i < 5; i++) {
                if (i < filledStars) {
                    starsHtml += '⭐';
                } else if (i === filledStars && halfStar) {
                    starsHtml += '⭐';
                } else {
                    starsHtml += '☆';
                }
            }
            
            communityStars.textContent = starsHtml;
            ratingValue.textContent = rating.toFixed(1);
            ratingCount.textContent = `(${stats.rating.count} ratings)`;
        }
        
        // Update horror metrics
        if (stats.stats) {
            updateMetricBar('gore', stats.stats.gore);
            updateMetricBar('fear', stats.stats.fear * 10); // Convert 0-10 to percentage
            updateMetricBar('kill', Math.min(stats.stats.kills * 4, 100)); // Convert kills to percentage
        }
        
        // Update recent reviews
        updateRecentReviews(stats.reviews || []);
    }
}

function updateMetricBar(type, value) {
    const valueElement = document.getElementById(`${type}-value`);
    const barElement = document.getElementById(`${type}-bar`);
    
    if (valueElement && barElement) {
        if (type === 'fear') {
            valueElement.textContent = `${(value/10).toFixed(1)}/10`;
        } else if (type === 'kill') {
            valueElement.textContent = Math.round(value/4);
        } else {
            valueElement.textContent = `${Math.round(value)}%`;
        }
        
        barElement.style.width = `${Math.min(value, 100)}%`;
    }
}

function updateRecentReviews(reviews) {
    const recentReviews = document.getElementById('recent-reviews');
    
    if (!recentReviews) return;
    
    if (reviews.length === 0) {
        recentReviews.innerHTML = `
            <div class="review-item">
                <div class="review-text">No reviews yet. Be the first!</div>
            </div>
        `;
    } else {
        const reviewsHtml = reviews.map(review => `
            <div class="review-item">
                <div class="review-text">"${review.text}"</div>
                <div class="review-meta">by ${review.user} • ${formatDate(review.timestamp)}</div>
            </div>
        `).join('');
        
        recentReviews.innerHTML = reviewsHtml;
    }
}

// ===== THEATER RELEASES =====
async function loadTheaterReleases() {
    try {
        const response = await fetch(`${API_BASE}/theater-releases`);
        const data = await response.json();
        
        const theaterSection = document.getElementById('theater-section-dynamic');
        if (!theaterSection) return;
        
        if (data.releases && data.releases.length > 0) {
            const releasesHtml = `
                <h3 class="text-center text-sm font-bold text-white mb-2" style="text-shadow: 0 0 10px rgba(255, 0, 0, 0.8); animation: pulse 2s infinite;">🎬 NOW IN THEATERS 🎬</h3>
                ${data.releases.map(movie => `
                    <div class="theater-item" onclick="searchMovie('${movie.title}')">
                        ${movie.poster_path ? 
                            `<img src="https://image.tmdb.org/t/p/w200${movie.poster_path}" 
                                 alt="${movie.title}" 
                                 class="theater-poster"
                                 onerror="this.src='https://via.placeholder.com/50x75/000000/FF0000?text=No+Poster'">` 
                            : ''}
                        <div class="theater-info">
                            <div class="theater-title">${movie.title}</div>
                            <div class="theater-date">${formatDate(movie.release_date)}</div>
                            ${movie.vote_average ? `<div class="theater-rating">⭐ ${movie.vote_average.toFixed(1)}</div>` : ''}
                        </div>
                    </div>
                `).join('')}
            `;
            
            theaterSection.innerHTML = releasesHtml;
        } else {
            theaterSection.innerHTML = `
                <h3 class="text-center text-sm font-bold text-white mb-2">🎬 NOW IN THEATERS 🎬</h3>
                <div class="text-center text-gray-400 text-xs">No current horror releases found</div>
            `;
        }
    } catch (error) {
        console.error('Error loading theater releases:', error);
        const theaterSection = document.getElementById('theater-section-dynamic');
        if (theaterSection) {
            theaterSection.innerHTML = `
                <h3 class="text-center text-sm font-bold text-white mb-2">🎬 NOW IN THEATERS 🎬</h3>
                <div class="text-center text-gray-400 text-xs">Unable to load theater releases</div>
            `;
        }
    }
}

// ===== OBSCURE GEMS =====
function loadDailyObscureGems() {
    const obscureGems = [
        {
            title: "Lake Mungo",
            year: "2008",
            poster: "https://picsum.photos/150/200?random=1",
            trailer: "https://www.youtube.com/embed/nAGZekCl8tA",
            amazon: "https://www.amazon.com/s?k=Lake+Mungo+DVD"
        },
        {
            title: "The House of the Devil", 
            year: "2009",
            poster: "https://picsum.photos/150/200?random=2",
            trailer: "https://www.youtube.com/embed/8Z_VkodeReY",
            amazon: "https://www.amazon.com/s?k=House+of+the+Devil+DVD"
        },
        {
            title: "Session 9",
            year: "2001", 
            poster: "https://picsum.photos/150/200?random=3",
            trailer: "https://www.youtube.com/embed/0yaq_mKG3b4",
            amazon: "https://www.amazon.com/s?k=Session+9+DVD"
        },
        {
            title: "The Blackcoat's Daughter",
            year: "2015",
            poster: "https://picsum.photos/150/200?random=4",
            trailer: "https://www.youtube.com/embed/8z_bSyOaZDA",
            amazon: "https://www.amazon.com/s?k=Blackcoats+Daughter+DVD"
        }
    ];
    
    // Pick 2 random gems for today
    const shuffled = obscureGems.sort(() => 0.5 - Math.random());
    const todaysGems = shuffled.slice(0, 2);
    
    const obscureGrid = document.querySelector('.obscure-movies-grid');
    if (obscureGrid) {
        obscureGrid.innerHTML = todaysGems.map(gem => `
            <div class="obscure-movie-item" data-trailer="${gem.trailer}">
                <img src="${gem.poster}" class="obscure-poster" alt="${gem.title}" 
                     onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjIyIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZmMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkhPUlJPUjwvdGV4dD48L3N2Zz4='">
                <iframe class="obscure-video" src="" frameborder="0" allowfullscreen></iframe>
                <div class="obscure-title">${gem.title}</div>
                <div class="obscure-year">${gem.year}</div>
                <a href="${gem.amazon}" target="_blank" class="dvd-link">Buy DVD</a>
            </div>
        `).join('');
        
        // Add click handlers for trailers
        document.querySelectorAll('.obscure-movie-item').forEach(item => {
            item.addEventListener('click', function() {
                const trailerUrl = this.dataset.trailer;
                if (trailerUrl) {
                    openVideoModal(trailerUrl);
                }
            });
        });
    }
}

// ===== VIDEO MODAL =====
function openVideoModal(videoUrl) {
    if (videoIframe && videoModal) {
        videoIframe.src = videoUrl;
        videoModal.style.display = 'flex';
    }
}

function closeVideoModal() {
    if (videoIframe && videoModal) {
        videoIframe.src = '';
        videoModal.style.display = 'none';
    }
}

// ===== UTILITY FUNCTIONS =====
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
    });
}

function showToast(message) {
    // Create simple toast notification
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Fade out after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

function showNotImplemented(feature) {
    showToast(`${feature} coming soon!`);
}

function showAboutModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-gray-900 border border-red-600 rounded-lg p-6 max-w-md text-center">
            <h2 class="text-red-500 text-2xl font-bold mb-4 nosifer">Horror Oracle</h2>
            <p class="text-gray-300 mb-4">Your gateway to the darkest depths of cinema. I possess knowledge of every horror film ever created.</p>
            <p class="text-gray-400 text-sm mb-4">Built with Flask, OpenAI, and a passion for horror movies.</p>
            <button onclick="this.parentElement.parentElement.remove()" 
                    class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors">
                Close
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

async function toggleRecentReleases() {
    showToast('Loading recent releases...');
    
    try {
        const response = await fetch(`${API_BASE}/recent-releases`);
        const data = await response.json();
        
        if (data.releases && data.releases.length > 0) {
            const message = `Recent Horror Releases:\n${data.releases.slice(0, 5).map(movie => 
                `• ${movie.title} (${formatDate(movie.release_date)})`
            ).join('\n')}`;
            
            addChatMessage('bot', message.replace(/\n/g, '<br>'));
        } else {
            addChatMessage('bot', 'No recent horror releases found.');
        }
    } catch (error) {
        console.error('Error loading recent releases:', error);
        showToast('Failed to load recent releases');
    }
}

// ===== BLOOD EFFECTS =====
function startBloodEffects() {
    // Initial burst and occasional cascades of 10 drops
    createBloodDrops(10);
    setInterval(() => createBloodDrops(10), 15000 + Math.random() * 30000); // Every 15-45 seconds
}

function createBloodDrops(count) {
    for (let i = 0; i < count; i++) {
        // Stagger each drop for a natural cascade
        setTimeout(createBloodDrop, i * (80 + Math.random() * 120));
    }
}

function createBloodDrop() {
    const drop = document.createElement('div');
    drop.className = 'blood-drop';
    
    // Random position at top of screen
    drop.style.left = Math.random() * 100 + 'vw';
    drop.style.width = (Math.random() * 10 + 5) + 'px';
    drop.style.height = (Math.random() * 15 + 10) + 'px';
    
    document.body.appendChild(drop);
    
    // Remove after animation
    setTimeout(() => {
        if (drop.parentNode) {
            drop.parentNode.removeChild(drop);
        }
    }, 7000);
}

// ===== TRAILER EMBED LOGIC =====
function showTrailer(youtubeUrl) {
    const videoId = extractYouTubeId(youtubeUrl);
    if (!videoId) return alert('Trailer not found.');
    const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
    const trailerContainer = document.getElementById('trailer-frame-container');
    const trailerIframe = document.getElementById('trailer-iframe');
    if(trailerIframe) {
        trailerIframe.src = embedUrl;
        trailerContainer.style.display = 'flex';
    }
}

function extractYouTubeId(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
}

function hideTrailer() {
    const trailerContainer = document.getElementById('trailer-frame-container');
    const trailerIframe = document.getElementById('trailer-iframe');
    if(trailerIframe) trailerIframe.src = '';
    if(trailerContainer) trailerContainer.style.display = 'none';
}

// ===== GENRE BUTTON FUNCTIONALITY =====
function setupGenreButtons() {
    // Get all the red genre buttons
    const genreButtons = document.querySelectorAll('.horror-genre-tag');
    
    genreButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the text and convert to API format
            const genreText = this.textContent.trim();
            
            // Map button text to API genre names
            const genreMap = {
                'SLASHERS': 'slashers',
                'ZOMBIES': 'zombies', 
                'VAMPIRES': 'vampires',
                'GORE FESTS': 'gore-fests',
                'SUPERNATURAL': 'supernatural',
                'DEMONS': 'demons',
                'PSYCHO KILLERS': 'psycho-killers',
                'ALIEN HORROR': 'alien-horror',
                'CREATURE FEATURES': 'creature-features',
                'HAUNTED HOUSES': 'haunted-houses',
                'PSYCHOLOGICAL': 'psychological',
                'CULT HORROR': 'cult-horror'
            };
            
            // Clean the text (remove emojis and extra spaces)
            const cleanGenre = genreText.replace(/[^\w\s]/g, '').trim();
            const apiGenre = genreMap[cleanGenre];
            
            if (apiGenre) {
                // Add visual feedback
                this.classList.add('pulse-once');
                
                // Call the genre API
                fetchGenreMovie(apiGenre);
            }
        });
    });
}

async function fetchGenreMovie(genre) {
    if (isLoading) return;
    
    isLoading = true;
    
    // Show loading message
    const loadingId = addChatMessage('bot', `Summoning a ${genre.replace('-', ' ')} movie from the depths...`, null, true);
    
    try {
        const response = await fetch(`${API_BASE}/random-genre/${genre}`);
        const data = await response.json();
        
        // Remove loading message
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();
        
        if (data.error) {
            addChatMessage('bot', `Error: ${data.error}`);
        } else {
            // Add Oracle's response - prevent duplicates
            const isDuplicate = data.movie_details && 
                   data.movie_details.title &&
                   lastDisplayedMovie === data.movie_details.title;
            
            if (!isDuplicate) {
                addChatMessage('bot', data.response, data.movie_details);
                lastDisplayedMovie = data.movie_details ? data.movie_details.title : null;
            }
            
            // Update movie sections
            if (data.movie_details && data.movie_details.title) {
                currentMovie = data.movie_details.title;
                currentMovieDetails = data.movie_details;
                updateMovieSections(data.movie_details, data.recommendations);
                loadMovieStats(currentMovie);
            }
        }
    } catch (error) {
        console.error('Genre fetch error:', error);
        
        // Remove loading message
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) loadingElement.remove();
        
        addChatMessage('bot', 'The spirits are restless... Please try again.');
    }
    
    isLoading = false;
}

// ===== AI-ADAPTIVE QUIZ: Horror DNA Display =====
function loadHorrorDNADisplay() {
    const quizHistory = JSON.parse(localStorage.getItem('horror-quiz-history') || '[]');
    
    if (quizHistory.length === 0) {
        return; // Keep default values
    }
    
    // Update quiz count
    const quizCountEl = document.getElementById('dna-quiz-count');
    if (quizCountEl) {
        quizCountEl.textContent = quizHistory.length;
    }
    
    // Calculate average fear tolerance (based on scores)
    const avgScore = quizHistory.reduce((sum, q) => sum + (q.score / q.total), 0) / quizHistory.length;
    const fearTolerance = Math.round(50 + (avgScore * 50)); // 50-100 range
    
    const fearToleranceEl = document.getElementById('dna-fear-tolerance');
    if (fearToleranceEl) {
        fearToleranceEl.textContent = `${fearTolerance}%`;
    }
    
    // Extract unique themes
    const themes = [...new Set(quizHistory.map(q => q.theme).filter(Boolean))];
    const themesEl = document.getElementById('dna-themes');
    if (themesEl && themes.length > 0) {
        themesEl.innerHTML = themes.slice(0, 3).map(theme => 
            `<span class="inline-block px-2 py-1 bg-green-950 rounded text-xs mr-1 mb-1">${theme}</span>`
        ).join('');
    }
}

// ===== PHASE 1: PERSONALIZATION FUNCTIONS =====

// PHASE 1: Handle genre click with tracking
async function handleGenreClick(genre) {
    // Hide the initial horror image when user clicks a genre
    const initialImage = document.getElementById('initial-horror-image');
    if (initialImage) {
        initialImage.style.display = 'none';
    }
    
    // Get current user from localStorage
    const savedUser = localStorage.getItem('horrorUser');
    
    if (savedUser) {
        const userObject = JSON.parse(savedUser);
        
        // Track genre preference
        try {
            await fetch(`${API_BASE}/track-genre-preference`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    googleId: userObject.sub,
                    genre: genre
                })
            });
            
            // Reload profile and recommendations
            loadHorrorProfile(userObject.sub);
            loadPersonalizedRecommendations(userObject.sub);
        } catch (error) {
            console.error('Error tracking genre preference:', error);
        }
    }
    
    // Continue with existing genre functionality
    fetchGenreMovie(genre);
}

// PHASE 1: Load and display horror profile
async function loadHorrorProfile(googleId) {
    try {
        const response = await fetch(`${API_BASE}/get-horror-profile`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({googleId: googleId})
        });
        const data = await response.json();
        
        if (data.horror_profile) {
            // Show profile section
            const profileSection = document.getElementById('horror-profile-section');
            if (profileSection) {
                profileSection.classList.remove('hidden');
                
                // Set profile name
                const profileName = document.getElementById('profile-name');
                if (profileName) {
                    profileName.textContent = data.horror_profile;
                }
                
                // Set icon based on profile
                const profileIcons = {
                    "Slasher Fan": "🔪",
                    "Zombie Enthusiast": "🧟",
                    "Vampire Lover": "🧛",
                    "Gore Hound": "💉",
                    "Supernatural Seeker": "👻",
                    "Demon Hunter": "😈",
                    "Psycho Thriller Fan": "🔫",
                    "Sci-Fi Horror Fan": "👽",
                    "Monster Movie Buff": "🦖",
                    "Haunted House Explorer": "🏚️",
                    "Mind Bender": "🧠",
                    "Cult Classic Connoisseur": "🕯️",
                    "Horror Enthusiast": "🎃",
                    "New Horror Fan": "🎃"
                };
                
                const icon = profileIcons[data.horror_profile] || "🎃";
                const profileIcon = document.getElementById('profile-icon');
                if (profileIcon) {
                    profileIcon.textContent = icon;
                }
            }
            
            // Highlight favorite genre tag
            if (data.genre_searches) {
                reorderGenreTags(data.genre_searches);
            }
        }
    } catch (error) {
        console.error('Error loading horror profile:', error);
    }
}

// PHASE 1: Load personalized recommendations
async function loadPersonalizedRecommendations(googleId) {
    try {
        const response = await fetch(`${API_BASE}/get-personalized-recommendations`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({googleId: googleId})
        });
        const data = await response.json();
        
        if (data.recommendations && data.recommendations.length > 0) {
            // Update title to "FOR YOU"
            const recsTitle = document.getElementById('recommendations-title');
            if (recsTitle) {
                recsTitle.textContent = 'FOR YOU';
            }
            
            // Update subtitle
            const subtitle = document.getElementById('for-you-subtitle');
            if (subtitle) {
                subtitle.textContent = `Because you love ${data.based_on_genre}`;
                subtitle.classList.remove('hidden');
            }
            
            // Display recommendations
            updateRecommendations(data.recommendations);
        }
    } catch (error) {
        console.error('Error loading personalized recommendations:', error);
    }
}

// PHASE 1: Highlight favorite genre tag
function reorderGenreTags(genreSearches) {
    if (!genreSearches || Object.keys(genreSearches).length === 0) return;
    
    // Find top genre
    let topGenre = null;
    let maxCount = 0;
    for (const [genre, count] of Object.entries(genreSearches)) {
        if (count > maxCount) {
            maxCount = count;
            topGenre = genre;
        }
    }
    
    if (!topGenre) return;
    
    // Map genre names to button text
    const genreMap = {
        'slashers': 'SLASHERS',
        'zombies': 'ZOMBIES',
        'vampires': 'VAMPIRES',
        'gore-fests': 'GORE FESTS',
        'supernatural': 'SUPERNATURAL',
        'demons': 'DEMONS',
        'psycho-killers': 'PSYCHO KILLERS',
        'alien-horror': 'ALIEN HORROR',
        'creature-features': 'CREATURE FEATURES',
        'haunted-houses': 'HAUNTED HOUSES',
        'psychological': 'PSYCHOLOGICAL',
        'cult-horror': 'CULT HORROR'
    };
    
    const searchText = genreMap[topGenre];
    if (!searchText) return;
    
    // Find and highlight the tag
    const genreTags = document.querySelectorAll('.horror-genre-tag');
    genreTags.forEach(tag => {
        const tagText = tag.textContent.replace(/[^\w\s]/g, '').trim();
        if (tagText === searchText) {
            tag.classList.add('favorite');
        } else {
            tag.classList.remove('favorite');
        }
    });
}

// ===========================
// HORROR ORACLE QUIZ HANDLER
// ===========================
console.log("🧠 Horror Oracle: Initializing quiz system...");

// Simplified quiz handler - matches user's provided code structure
async function startQuizHandler() {
  console.log("🎬 Starting quiz...");
  try {
    const response = await fetch(`${API_BASE}/api/start_quiz`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    console.log("✅ Quiz data loaded:", data);
    // Backend returns quiz data directly with questions array
    if (data.questions && data.questions.length > 0) {
      renderQuizHandler(data);
    } else if (data.quiz) {
      renderQuizHandler(data.quiz);
    } else {
      console.warn("⚠️ No quiz data found:", data);
    }
  } catch (err) {
    console.error("❌ Failed to start quiz:", err);
    alert("Server connection failed. Restart Horror Oracle backend.");
  }
}

async function submitAnswersHandler(answers) {
  console.log("📤 Submitting answers...");
  try {
    // Get user ID for submission
    const savedUser = localStorage.getItem('horrorUser');
    let userId = 'guest';
    if (savedUser) {
      try {
        const userObject = JSON.parse(savedUser);
        userId = userObject.sub || userObject.email || 'guest';
      } catch (e) {
        console.error('Error parsing user:', e);
      }
    }
    
    const response = await fetch(`${API_BASE}/api/submit_answers`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ 
        userId: userId,
        answers: answers,
        quiz: window.currentQuiz || {} // Include current quiz context if available
      })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    console.log("🏁 Results received:", result);
    showResultsHandler(result);
  } catch (err) {
    console.error("❌ Failed to submit answers:", err);
    alert("Something went wrong while submitting. Check backend logs.");
  }
}

function renderQuizHandler(quiz) {
  console.log("🎨 Rendering quiz...");
  // Store quiz globally for submission context
  window.currentQuiz = quiz;
  
  // Use existing render functions if available
  if (typeof renderQuiz === 'function') {
    renderQuiz(quiz);
  } else if (typeof displayQuizWithData === 'function') {
    displayQuizWithData(quiz);
  } else {
    console.error("❌ No quiz render function available");
  }
}

function showResultsHandler(result) {
  console.log("📊 Displaying results...");
  // Use existing results functions if available
  if (typeof showResults === 'function') {
    showResults(result);
  } else if (typeof displayOracleResults === 'function') {
    displayOracleResults(result);
  } else {
    console.error("❌ No results display function available");
  }
}

// Automatically bind to the start button when DOM is ready
// Matches user's selector: [id*="Face"],[id*="start"],[id*="Trial"]
function bindQuizStartButton() {
  const startButton = document.querySelector('[id*="Face"],[id*="start"],[id*="Trial"]');
  if (startButton) {
    // Only bind if not already bound
    if (!startButton.hasAttribute('data-quiz-handler-bound')) {
      startButton.setAttribute('data-quiz-handler-bound', 'true');
      startButton.addEventListener('click', function(e) {
        // Don't prevent default if button has existing onclick handler
        if (!startButton.onclick) {
          startQuizHandler();
          e.preventDefault();
        }
      });
      console.log("✅ Quiz handler bound to button:", startButton.id || startButton.className);
    }
  } else {
    console.warn("⚠️ Quiz start button not found");
  }
}

// Bind when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bindQuizStartButton);
} else {
  bindQuizStartButton();
}

// Export handlers with user's preferred names (if they don't conflict)
// Note: These won't override existing functions, but can be called directly
window.startQuizHandler = startQuizHandler;
window.submitAnswersHandler = submitAnswersHandler;

// Store references to existing functions before we define new ones
const _originalStartQuiz = window.startQuiz;
const _originalSubmitAnswers = window.submitAnswers;

/**
 * Simplified quiz starter - fetches quiz from backend and renders it
 * Uses existing displayQuizWithData() for rendering
 * This version can be called without parameters (unlike the original)
 */
async function startQuiz() {
  console.log("🎬 Starting quiz...");
  try {
    // Get user ID
    const savedUser = localStorage.getItem('horrorUser');
    let userId = 'guest';
    if (savedUser) {
      try {
        const userObject = JSON.parse(savedUser);
        userId = userObject.sub || userObject.email || 'guest';
      } catch (e) {
        console.error('Error parsing user:', e);
      }
    }
    
    const response = await fetch(`${API_BASE}/api/start_quiz`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ user_id: userId, force_new: true })
    });
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    console.log("✅ Quiz data loaded:", data);
    
    // Transform backend format to format expected by displayQuizWithData
    const quizData = {
      questions: data.questions || [],
      theme: data.theme || 'Horror Oracle',
      difficulty: data.difficulty || 'intermediate',
      nextQuizNumber: 1,
      oracleData: data,  // Store full Oracle Engine response
      room: data.room,
      intro: data.intro,
      lore: data.lore,
      player_profile: data.player_profile,
      oracle_state: data.oracle_state
    };
    
    // Use existing render function
    renderQuiz(quizData);
  } catch (err) {
    console.error("❌ Failed to start quiz:", err);
    alert("Server connection failed. Restart the Horror Oracle backend.");
  }
}

/**
 * Render quiz using existing displayQuizWithData function
 * @param {Object} quiz - Quiz data object
 */
function renderQuiz(quiz) {
  console.log("🎨 Rendering quiz...");
  
  // Ensure blood quiz modal is open
  if (!document.getElementById('bloodQuizModal')) {
    console.warn("⚠️ Blood quiz modal not found, attempting to open...");
    // Try to trigger the quiz modal - this depends on your existing UI
    if (typeof openBloodQuiz === 'function') {
      openBloodQuiz();
    }
  }
  
  // Use existing displayQuizWithData function
  if (typeof displayQuizWithData === 'function') {
    displayQuizWithData(quiz);
  } else {
    console.error("❌ displayQuizWithData function not found!");
    alert("Quiz rendering function not available. Check console for errors.");
  }
}

/**
 * Submit answers to backend and show results
 * @param {Object|Array} answers - Answers object or array
 */
async function submitAnswers(answers) {
  console.log("📤 Submitting answers...");
  try {
    // Use original submitAnswers function if it exists and handles the format
    if (typeof _originalSubmitAnswers === 'function') {
      const result = answers ? await _originalSubmitAnswers(answers) : await _originalSubmitAnswers();
      console.log("🏁 Results received:", result);
      showResults(result);
      return;
    }
    
    // Fallback: direct API call
    const savedUser = localStorage.getItem('horrorUser');
    let userId = 'guest';
    if (savedUser) {
      try {
        const userObject = JSON.parse(savedUser);
        userId = userObject.sub || userObject.email || 'guest';
      } catch (e) {
        console.error('Error parsing user:', e);
      }
    }
    
    // Convert answers format if needed
    let answersDict = {};
    if (answers) {
      if (Array.isArray(answers)) {
        answers.forEach((answer, index) => {
          answersDict[`q${index}`] = answer.selected || answer.answer || answer;
        });
      } else if (typeof answers === 'object') {
        answersDict = answers;
      }
    } else if (currentQuiz && currentQuiz.answers) {
      currentQuiz.answers.forEach((answer, index) => {
        answersDict[`q${index}`] = answer.selected || answer.answer || answer;
      });
    }
    
    const response = await fetch(`${API_BASE}/api/submit_answers`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ 
        user_id: userId,
        quiz: currentQuiz.oracleData || {},
        answers: answersDict 
      })
    });
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    console.log("🏁 Results received:", result);
    showResults(result);
  } catch (err) {
    console.error("❌ Failed to submit answers:", err);
    alert("Something went wrong while submitting. Check backend logs.");
  }
}

/**
 * Show quiz results using existing displayOracleResults function
 * @param {Object} result - Results object from backend
 */
function showResults(result) {
  console.log("📊 Displaying results...");
  
  // Use existing displayOracleResults function
  if (typeof displayOracleResults === 'function') {
    displayOracleResults(result);
  } else {
    // Fallback: simple results display
    const quizContent = document.getElementById('quizContent') || document.getElementById('quizBody');
    if (quizContent) {
      quizContent.innerHTML = `
        <div class="text-center p-6">
          <h2 class="text-3xl font-bold text-red-500 mb-4">Quiz Results</h2>
          <p class="text-2xl mb-2">${result.score || 0}/${result.out_of || 0}</p>
          <p class="text-lg text-gray-300">${result.percentage || 0}% Correct</p>
          ${result.evaluation && result.evaluation.oracle_reaction ? `
            <div class="mt-4 p-4 bg-red-900 bg-opacity-30 rounded">
              <p class="text-yellow-400">${result.evaluation.oracle_reaction}</p>
            </div>
          ` : ''}
        </div>
      `;
    }
  }
}

// Hook into button — Cursor must detect the ID automatically.
// Wait for DOM to be ready before attaching event listeners
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', attachQuizStarterListeners);
} else {
  attachQuizStarterListeners();
}

function attachQuizStarterListeners() {
  // Find buttons with IDs containing "start" or "Face"
  const startButtons = document.querySelectorAll('[id*="start" i], [id*="Face" i]');
  
  startButtons.forEach(button => {
    // Check if button already has onclick or other listeners
    if (!button.hasAttribute('data-quiz-starter-attached')) {
      button.setAttribute('data-quiz-starter-attached', 'true');
      button.addEventListener('click', function(e) {
        // Only trigger if no existing onclick handler
        if (!button.onclick && !e.defaultPrevented) {
          console.log("🎯 Quiz starter triggered from button:", button.id);
          startQuiz();
        }
      });
    }
  });
  
  // Also check for the specific "Face Your Nightmares" button
  const nightmareBtn = document.getElementById('nightmare-quiz-btn');
  if (nightmareBtn && !nightmareBtn.hasAttribute('data-quiz-starter-attached')) {
    // Note: This button already has onclick="startOracleQuiz()", so we won't override it
    // But we can add it as an alias
    console.log("🎯 Found nightmare-quiz-btn (already has handler)");
  }
  
  console.log(`✅ Quiz starter listeners attached to ${startButtons.length} button(s)`);
}