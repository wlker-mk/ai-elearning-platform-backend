#!/usr/bin/env python3
"""
script2_apply_full_schemas.py

Option A1:
- Parcourt ./microservices/<service>/prisma/schema.prisma
- Si schema.prisma n'existe pas -> crée le fichier avec le schéma complet du service
- Si schema.prisma existe et contient un placeholder (détecté par 'model Example' ou 'DEFAULT PRISMA SCHEMA (placeholder)')
    -> le remplace par le schéma complet du service
- Si schema.prisma existe et semble réel (ne contient pas 'model Example' ni 'DEFAULT PRISMA SCHEMA (placeholder)') -> ne le touche pas
- Ignore les services marqués no_prisma (cache-service, api-gateway)
"""

from pathlib import Path
import sys

# ----------------------------
# CONFIG : liste des services
# ----------------------------
MICROSERVICES = {
    'auth-service': {},
    'user-service': {},
    'courses-service': {},
    'quizzes-service': {},
    'bookings-service': {},
    'payments-service': {},
    'notifications-service': {},
    'webinars-service': {},
    'gamification-service': {},
    'chatbot-service': {},
    'analytics-service': {},
    'communications-service': {},
    'search-service': {},
    'storage-service': {},
    'security-service': {},
    'monitoring-service': {},
    'ai-gateway': {},
    'cache-service': {'no_prisma': True},
    'api-gateway': {'no_prisma': True},
    'i18n-service': {},
    'sponsors-service': {},
    'enrollment-service': {},
    'reviews-service': {},
}

# ----------------------------
# Header commun (factorisé)
# ----------------------------
COMMON_HEADER = '''generator client {
  provider = "prisma-client-py"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}
'''

# ----------------------------
# Schémas complets par service
# (ces fonctions retournent le contenu complet du schema.prisma)
# ----------------------------

def schema_auth():
    return COMMON_HEADER + r'''
// AUTH SERVICE - Users, Sessions, MFA, OAuth

enum UserRole {
  SUPER_ADMIN
  ADMIN
  MODERATOR
  INSTRUCTOR
  STUDENT
  STUDENT_PREMIUM
  TEACHING_ASSISTANT
  CONTENT_REVIEWER
  SUPPORT
}

enum AuthType {
  PASSWORD
  GOOGLE
  GITHUB
  FACEBOOK
  LINKEDIN
  MICROSOFT
  APPLE
  SSO_ENTERPRISE
  SAML
  OAUTH2
}

model User {
  id                  String    @id @default(uuid())
  username            String    @unique
  email               String    @unique
  passwordHash        String
  role                UserRole  @default(STUDENT)

  isEmailVerified     Boolean   @default(false)
  isPhoneVerified     Boolean   @default(false)
  emailVerificationToken String?
  emailVerificationExpires DateTime?

  isActive            Boolean   @default(true)
  isSuspended         Boolean   @default(false)
  suspensionReason    String?

  mfaEnabled          Boolean   @default(false)
  mfaSecret           String?
  backupCodes         String[]

  lastLoginAt         DateTime?
  lastLoginIp         String?
  failedLoginAttempts Int       @default(0)
  lockedUntil         DateTime?

  resetPasswordToken  String?
  resetPasswordExpires DateTime?

  authProvider        AuthType  @default(PASSWORD)
  authProviderId      String?

  createdAt           DateTime  @default(now())
  updatedAt           DateTime  @updatedAt

  sessions            Session[]
  refreshTokens       RefreshToken[]
  loginHistory        LoginHistory[]

  @@index([email, username])
  @@map("users")
}

model Session {
  id              String    @id @default(uuid())
  userId          String
  token           String    @unique
  expiresAt       DateTime
  ipAddress       String?
  userAgent       String?
  device          String?
  isValid         Boolean   @default(true)
  createdAt       DateTime  @default(now())
  @@index([userId, isValid])
  @@map("sessions")
}

model RefreshToken {
  id              String    @id @default(uuid())
  userId          String
  token           String    @unique
  expiresAt       DateTime
  isRevoked       Boolean   @default(false)
  revokedAt       DateTime?
  deviceId        String?
  ipAddress       String?
  createdAt       DateTime  @default(now())
  @@index([userId, isRevoked])
  @@map("refresh_tokens")
}

model LoginHistory {
  id              String    @id @default(uuid())
  userId          String
  success         Boolean
  failureReason   String?
  ipAddress       String?
  userAgent       String?
  location        String?
  country         String?
  city            String?
  device          String?
  browser         String?
  os              String?
  loginAt         DateTime  @default(now())
  @@index([userId, loginAt])
  @@map("login_history")
}
'''

def schema_user():
    return COMMON_HEADER + r'''
// USER SERVICE - Profiles, Students, Instructors, Preferences, Country

model UserProfile {
  id              String    @id @default(uuid())
  userId          String    @unique
  firstName       String
  lastName        String
  phoneNumber     String?
  dateOfBirth     DateTime?
  profileImageUrl String?
  coverImageUrl   String?
  bio             String?   @db.Text
  website         String?
  linkedin        String?
  github          String?
  twitter         String?
  facebook        String?
  country         String?
  city            String?
  timezone        String    @default("UTC")
  language        String    @default("en")
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([userId])
  @@map("user_profiles")
}

model Student {
  id                  String   @id @default(uuid())
  userId              String   @unique
  studentCode         String   @unique
  points              Int      @default(0)
  level               Int      @default(1)
  experiencePoints    Int      @default(0)
  streak              Int      @default(0)
  maxStreak           Int      @default(0)
  lastActivityDate    DateTime?
  totalCoursesEnrolled Int     @default(0)
  totalCoursesCompleted Int    @default(0)
  totalLearningTime    Int     @default(0)
  totalCertificates    Int     @default(0)
  preferredCategories String[]
  createdAt           DateTime @default(now())
  updatedAt           DateTime @updatedAt
  @@index([studentCode])
  @@map("students")
}

model Instructor {
  id                  String   @id @default(uuid())
  userId              String   @unique
  instructorCode      String   @unique
  title               String?
  headline            String?
  specializations     String[]
  expertise           String[]
  certifications      String[]
  yearsOfExperience   Int      @default(0)
  hourlyRate          Float?
  rating              Float?   @default(0)
  totalReviews        Int      @default(0)
  totalStudents       Int      @default(0)
  totalCourses        Int      @default(0)
  isVerified          Boolean  @default(false)
  verifiedAt          DateTime?
  bankAccount         String?
  bankName            String?
  paypalEmail         String?
  createdAt           DateTime @default(now())
  updatedAt           DateTime @updatedAt
  @@index([instructorCode, isVerified])
  @@map("instructors")
}

model UserPreference {
  id                  String   @id @default(uuid())
  userId              String   @unique
  theme               String   @default("light")
  language            String   @default("en")
  timezone            String   @default("UTC")
  currency            String   @default("USD")
  emailNotifications  Boolean  @default(true)
  pushNotifications   Boolean  @default(true)
  smsNotifications    Boolean  @default(false)
  createdAt           DateTime @default(now())
  updatedAt           DateTime @updatedAt
  @@index([userId])
  @@map("user_preferences")
}

model Country {
  id              String    @id @default(uuid())
  name            String
  code            String    @unique
  code3           String    @unique
  phoneCode       String
  currency        String
  currencySymbol  String
  flag            String?
  emoji           String?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([code])
  @@map("countries")
}
'''

def schema_courses():
    return COMMON_HEADER + r'''
// COURSES SERVICE - Course, Section, Lesson, Category, Tag, Wishlist, CourseTag

enum CourseStatus {
  DRAFT
  PENDING_REVIEW
  IN_REVIEW
  APPROVED
  PUBLISHED
  ARCHIVED
  REJECTED
  UNPUBLISHED
}

enum CourseDifficulty {
  BEGINNER
  INTERMEDIATE
  ADVANCED
  EXPERT
  ALL_LEVELS
}

enum CourseType {
  VIDEO_COURSE
  TEXT_BASED
  MIXED
  LIVE_CLASS
  WORKSHOP
  BOOTCAMP
  CERTIFICATION_PREP
}

model Course {
  id                  String         @id @default(uuid())
  slug                String         @unique
  title               String
  subtitle            String?
  description         String         @db.Text
  instructorId        String
  categoryId          String
  tags                CourseTag[]
  language            String         @default("ENGLISH")
  difficulty          CourseDifficulty
  type                CourseType
  price               Float
  isFree              Boolean        @default(false)
  thumbnailUrl        String?
  estimatedDuration   Int
  enrollmentCount     Int            @default(0)
  completionCount     Int            @default(0)
  rating              Float?         @default(0)
  reviewCount         Int            @default(0)
  publishedAt         DateTime?
  createdAt           DateTime       @default(now())
  updatedAt           DateTime       @updatedAt
  sections            Section[]
  @@index([slug, instructorId])
  @@map("courses")
}

model Section {
  id              String    @id @default(uuid())
  courseId        String
  title           String
  description     String?   @db.Text
  order           Int
  duration        Int       @default(0)
  lessons         Lesson[]
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([courseId, order])
  @@map("sections")
}

model Lesson {
  id              String    @id @default(uuid())
  sectionId       String
  title           String
  description     String?   @db.Text
  content         String?   @db.Text
  order           Int
  videoUrl        String?
  videoDuration   Int?
  isFree          Boolean   @default(false)
  resources       Resource[]
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([sectionId, order])
  @@map("lessons")
}

model Resource {
  id              String    @id @default(uuid())
  lessonId        String
  title           String
  type            String
  url             String
  fileSize        Int?
  isDownloadable  Boolean   @default(true)
  downloadCount   Int       @default(0)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([lessonId])
  @@map("resources")
}

model Category {
  id              String    @id @default(uuid())
  name            String    @unique
  slug            String    @unique
  description     String?   @db.Text
  imageUrl        String?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("categories")
}

model Tag {
  id              String    @id @default(uuid())
  name            String    @unique
  slug            String    @unique
  usageCount      Int       @default(0)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("tags")
}

model CourseTag {
  id              String    @id @default(uuid())
  courseId        String
  tagId           String
  @@unique([courseId, tagId])
  @@map("course_tags")
}

model Wishlist {
  id              String    @id @default(uuid())
  studentId       String
  courseId        String
  addedAt         DateTime  @default(now())
  @@unique([studentId, courseId])
  @@map("wishlist")
}
'''

def schema_quizzes():
    return COMMON_HEADER + r'''
// QUIZZES SERVICE - Quiz, Question, QuizAttempt, Proctoring

enum QuizType {
  MULTIPLE_CHOICE
  TRUE_FALSE
  SHORT_ANSWER
  ESSAY
  CODING
  MATCHING
  FILL_BLANK
}

model Quiz {
  id              String    @id @default(uuid())
  lessonId        String
  courseId        String
  title           String
  description     String?   @db.Text
  duration        Int?
  passingScore    Float     @default(70)
  maxAttempts     Int       @default(3)
  randomizeQuestions Boolean @default(false)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  questions       Question[]
  @@index([lessonId, courseId])
  @@map("quizzes")
}

model Question {
  id              String    @id @default(uuid())
  quizId          String
  type            QuizType
  question        String    @db.Text
  order           Int
  points          Float     @default(1)
  options         Json?
  correctAnswer   Json?
  explanation     String?   @db.Text
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([quizId, order])
  @@map("questions")
}

model QuizAttempt {
  id              String    @id @default(uuid())
  quizId          String
  studentId       String
  attemptNumber   Int
  score           Float
  percentage      Float
  isPassed        Boolean
  answers         Json
  startedAt       DateTime
  submittedAt     DateTime?
  timeSpent       Int?
  createdAt       DateTime  @default(now())
  @@index([quizId, studentId])
  @@map("quiz_attempts")
}

model ProctoringSession {
  id              String    @id @default(uuid())
  quizAttemptId   String    @unique
  webcamUrl       String?
  screenUrl       String?
  audioUrl        String?
  faceDetections  Json?
  suspiciousActivity Json?
  tabSwitches     Int       @default(0)
  multipleFaces   Boolean   @default(false)
  noFaceDetected  Boolean   @default(false)
  copyPasteDetected Boolean @default(false)
  flaggedForReview Boolean  @default(false)
  reviewedBy      String?
  reviewedAt      DateTime?
  reviewNotes     String?   @db.Text
  startedAt       DateTime  @default(now())
  endedAt         DateTime?
  @@index([flaggedForReview])
  @@map("proctoring_sessions")
}
'''

def schema_bookings():
    return COMMON_HEADER + r'''
// BOOKINGS SERVICE - Booking, Meeting, Availability

enum MeetingType {
  ONE_ON_ONE
  GROUP_SESSION
  WEBINAR
  OFFICE_HOURS
  WORKSHOP
  MENTORING
}

enum BookingStatus {
  PENDING
  CONFIRMED
  CANCELLED
  COMPLETED
  NO_SHOW
  RESCHEDULED
}

model Booking {
  id              String        @id @default(uuid())
  studentId       String
  instructorId    String
  title           String
  description     String?       @db.Text
  type            MeetingType
  scheduledAt     DateTime
  duration        Int
  timezone        String
  status          BookingStatus @default(PENDING)
  meetingUrl      String?
  meetingId       String?
  password        String?
  cancelledBy     String?
  cancelReason    String?
  cancelledAt     DateTime?
  rescheduledFrom String?
  rescheduledTo   String?
  price           Float?
  isPaid          Boolean       @default(false)
  paymentId       String?
  studentNotes    String?       @db.Text
  instructorNotes String?       @db.Text
  remindersSent   Json?
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt
  @@index([studentId, instructorId, scheduledAt])
  @@map("bookings")
}

model Meeting {
  id              String      @id @default(uuid())
  bookingId       String?     @unique
  instructorId    String
  title           String
  description     String?     @db.Text
  type            MeetingType
  scheduledAt     DateTime
  duration        Int
  meetingUrl      String?
  meetingId       String?
  platform        String?
  isRecorded      Boolean     @default(false)
  recordingUrl    String?
  maxParticipants Int?        @default(1)
  participants    Json?
  startedAt       DateTime?
  endedAt         DateTime?
  createdAt       DateTime    @default(now())
  updatedAt       DateTime    @updatedAt
  @@index([instructorId, scheduledAt])
  @@map("meetings")
}

model InstructorAvailability {
  id              String     @id @default(uuid())
  instructorId    String
  dayOfWeek       Int        // 0-6
  startTime       String
  endTime         String
  isRecurring     Boolean    @default(true)
  effectiveFrom   DateTime?
  effectiveUntil  DateTime?
  specificDate    DateTime?
  isActive        Boolean    @default(true)
  createdAt       DateTime   @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([instructorId, dayOfWeek])
  @@map("instructor_availability")
}

model TimeSlot {
  id              String     @id @default(uuid())
  instructorId    String
  date            DateTime   @db.Date
  startTime       String
  endTime         String
  isAvailable     Boolean    @default(true)
  isBooked        Boolean    @default(false)
  bookingId       String?
  createdAt       DateTime   @default(now())
  @@unique([instructorId, date, startTime])
  @@map("time_slots")
}
'''

def schema_payments():
    return COMMON_HEADER + r'''
// PAYMENTS SERVICE - Payments, Transactions, Invoices, Subscriptions, Discounts

enum PaymentStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
  REFUNDED
  CANCELLED
  DISPUTED
  EXPIRED
}

enum PaymentMethod {
  CREDIT_CARD
  DEBIT_CARD
  PAYPAL
  STRIPE
  BANK_TRANSFER
  MOBILE_MONEY
  CRYPTO
  APPLE_PAY
  GOOGLE_PAY
}

enum SubscriptionType {
  FREE
  MONTHLY
  QUARTERLY
  SEMI_ANNUAL
  ANNUAL
  LIFETIME
  ENTERPRISE
  STUDENT
  TEAM
}

enum DiscountType {
  PERCENTAGE
  FIXED_AMOUNT
  BUNDLE
  EARLY_BIRD
  FLASH_SALE
}

model Payment {
  id                  String        @id @default(uuid())
  studentId           String
  amount              Float
  currency            String        @default("USD")
  method              PaymentMethod
  status              PaymentStatus @default(PENDING)
  transactionId       String?       @unique
  externalReference   String?
  gatewayResponse     Json?
  courseId            String?
  subscriptionId      String?
  items               Json?
  description         String?
  metadata            Json?
  processingFee       Float         @default(0)
  platformFee         Float         @default(0)
  netAmount           Float
  isRefunded          Boolean       @default(false)
  refundedAmount      Float?
  refundedAt          DateTime?
  paidAt              DateTime?
  createdAt           DateTime      @default(now())
  updatedAt           DateTime      @updatedAt
  @@index([studentId, status])
  @@map("payments")
}

model Transaction {
  id              String        @id @default(uuid())
  paymentId       String?
  type            String
  amount          Float
  currency        String        @default("USD")
  status          PaymentStatus
  fromAccount     String?
  toAccount       String?
  gatewayId       String?
  gatewayResponse Json?
  createdAt       DateTime      @default(now())
  @@index([paymentId])
  @@map("transactions")
}

model Invoice {
  id              String        @id @default(uuid())
  invoiceNumber   String        @unique
  studentId       String
  paymentId       String?
  subtotal        Float
  tax             Float         @default(0)
  discount        Float         @default(0)
  total           Float
  amountPaid      Float         @default(0)
  amountDue       Float
  currency        String        @default("USD")
  status          PaymentStatus @default(PENDING)
  items           Json
  issueDate       DateTime      @default(now())
  dueDate         DateTime
  paidAt          DateTime?
  pdfUrl          String?
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt
  @@index([studentId, status])
  @@index([invoiceNumber])
  @@map("invoices")
}

model Subscription {
  id              String           @id @default(uuid())
  studentId       String           @unique
  type            SubscriptionType
  startDate       DateTime
  endDate         DateTime
  trialEndDate    DateTime?
  isActive        Boolean          @default(true)
  isCancelled     Boolean          @default(false)
  cancelledAt     DateTime?
  price           Float
  currency        String           @default("USD")
  autoRenew       Boolean          @default(true)
  nextBillingDate DateTime?
  paymentMethod   PaymentMethod
  lastPaymentId   String?
  createdAt       DateTime         @default(now())
  updatedAt       DateTime         @updatedAt
  @@index([isActive, endDate])
  @@map("subscriptions")
}

model Discount {
  id              String        @id @default(uuid())
  code            String        @unique
  type            DiscountType
  value           Float
  startDate       DateTime
  endDate         DateTime
  maxUses         Int?
  usesCount       Int           @default(0)
  maxUsesPerUser  Int?          @default(1)
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt
  @@index([code])
  @@map("discounts")
}
'''

def schema_notifications():
    return COMMON_HEADER + r'''
// NOTIFICATIONS SERVICE - Preferences, Templates, Logs, Notifications

enum NotificationChannel {
  EMAIL
  PUSH
  SMS
  IN_APP
}

enum NotificationStatus {
  QUEUED
  SENT
  FAILED
  DELIVERED
  READ
}

model NotificationTemplate {
  id              String    @id @default(uuid())
  name            String    @unique
  channel         NotificationChannel
  subject         String?
  body            String    @db.Text
  variables       String[]
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("notification_templates")
}

model NotificationPreference {
  id              String    @id @default(uuid())
  userId          String    @unique
  emailEnabled    Boolean   @default(true)
  pushEnabled     Boolean   @default(true)
  smsEnabled      Boolean   @default(false)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("notification_preferences")
}

model OutgoingNotification {
  id              String    @id @default(uuid())
  templateId      String?
  userId          String?
  channel         NotificationChannel
  recipient       String
  payload         Json?
  status          NotificationStatus @default(QUEUED)
  attempts        Int       @default(0)
  lastAttemptAt   DateTime?
  sentAt          DateTime?
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([userId, status])
  @@map("outgoing_notifications")
}

model NotificationLog {
  id              String    @id @default(uuid())
  notificationId  String
  providerResponse Json?
  providerName    String?
  createdAt       DateTime  @default(now())
  @@index([notificationId])
  @@map("notification_logs")
}
'''

def schema_webinars():
    return COMMON_HEADER + r'''
// WEBINARS SERVICE - Webinars, Registrations, Sessions

enum WebinarStatus {
  DRAFT
  SCHEDULED
  LIVE
  ENDED
  CANCELLED
}

model Webinar {
  id              String    @id @default(uuid())
  title           String
  description     String?   @db.Text
  instructorId    String
  scheduledAt     DateTime
  durationMinutes Int
  capacity        Int?
  status          WebinarStatus @default(SCHEDULED)
  meetingUrl      String?
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("webinars")
}

model WebinarRegistration {
  id              String    @id @default(uuid())
  webinarId       String
  userId          String
  registeredAt    DateTime  @default(now())
  status          String    @default("CONFIRMED")
  joinUrl         String?
  createdAt       DateTime  @default(now())
  @@unique([webinarId, userId])
  @@map("webinar_registrations")
}
'''

def schema_gamification():
    return COMMON_HEADER + r'''
// GAMIFICATION SERVICE - Achievements, Leaderboards, Rewards, Quests

enum BadgeRarity {
  COMMON
  RARE
  EPIC
  LEGENDARY
  MYTHIC
}

model Badge {
  id              String    @id @default(uuid())
  name            String    @unique
  description     String?   @db.Text
  rarity          BadgeRarity @default(COMMON)
  imageUrl        String?
  points          Int       @default(10)
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("badges")
}

model StudentBadge {
  id              String    @id @default(uuid())
  studentId       String
  badgeId         String
  earnedAt        DateTime?
  createdAt       DateTime  @default(now())
  @@unique([studentId, badgeId])
  @@map("student_badges")
}

model Achievement {
  id              String    @id @default(uuid())
  name            String    @unique
  description     String?   @db.Text
  points          Int       @default(50)
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("achievements")
}

model Leaderboard {
  id              String    @id @default(uuid())
  name            String
  type            String
  metric          String
  startDate       DateTime?
  endDate         DateTime?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("leaderboards")
}

model LeaderboardEntry {
  id              String    @id @default(uuid())
  leaderboardId   String
  studentId       String
  rank            Int
  score           Float
  createdAt       DateTime  @default(now())
  @@unique([leaderboardId, studentId])
  @@map("leaderboard_entries")
}

model Reward {
  id              String    @id @default(uuid())
  name            String
  description     String?   @db.Text
  type            String
  pointsCost      Int
  totalQuantity   Int?
  remainingQuantity Int?
  imageUrl        String?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("rewards")
}

model RewardRedemption {
  id              String    @id @default(uuid())
  studentId       String
  rewardId        String
  pointsSpent     Int
  isFulfilled     Boolean   @default(false)
  fulfilledAt     DateTime?
  createdAt       DateTime  @default(now())
  @@map("reward_redemptions")
}

model Quest {
  id              String    @id @default(uuid())
  name            String
  description     String?   @db.Text
  rewardId        String?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  @@map("quests")
}
'''

def schema_chatbot():
    return COMMON_HEADER + r'''
// CHATBOT SERVICE - Conversations, Intents, Entities, KnowledgeBase

enum ConversationStatus {
  ACTIVE
  RESOLVED
  ESCALATED
  CLOSED
}

enum MessageRole {
  USER
  ASSISTANT
  SYSTEM
}

model Conversation {
  id              String    @id @default(uuid())
  userId          String
  status          ConversationStatus @default(ACTIVE)
  courseId        String?
  lessonId        String?
  primaryIntent   String?
  sentiment       Float?
  isResolved      Boolean   @default(false)
  resolvedAt      DateTime?
  startedAt       DateTime  @default(now())
  lastMessageAt   DateTime  @default(now())
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  messages        ChatMessage[]
  @@index([userId, status])
  @@map("conversations")
}

model ChatMessage {
  id              String    @id @default(uuid())
  conversationId  String
  role            MessageRole
  content         String    @db.Text
  model           String?
  tokens          Int?
  detectedIntent  String?
  confidence      Float?
  entities        Json?
  wasHelpful      Boolean?
  createdAt       DateTime  @default(now())
  @@index([conversationId, createdAt])
  @@map("chat_messages")
}

model Intent {
  id              String    @id @default(uuid())
  name            String    @unique
  type            String
  description     String?   @db.Text
  trainingPhrases String[]
  responses       String[]
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("intents")
}

model Entity {
  id              String    @id @default(uuid())
  name            String
  entityType      String
  values          Json
  synonyms        Json?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("entities")
}

model KnowledgeBase {
  id              String    @id @default(uuid())
  question        String    @db.Text
  answer          String    @db.Text
  category        String?
  tags            String[]
  keywords        String[]
  viewCount       Int       @default(0)
  helpfulCount    Int       @default(0)
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("knowledge_base")
}
'''

def schema_analytics():
    return COMMON_HEADER + r'''
// ANALYTICS SERVICE - UserActivity, RevenueReport, CourseAnalytics

model UserActivity {
  id              String    @id @default(uuid())
  userId          String
  eventType       String
  metadata        Json?
  createdAt       DateTime  @default(now())
  @@index([userId, eventType, createdAt])
  @@map("user_activity")
}

model RevenueReport {
  id              String    @id @default(uuid())
  date            DateTime  @db.Date
  totalRevenue    Float     @default(0)
  totalOrders     Int       @default(0)
  createdAt       DateTime  @default(now())
  @@unique([date])
  @@map("revenue_reports")
}

model CourseAnalytics {
  id              String    @id @default(uuid())
  courseId        String
  date            DateTime  @db.Date
  views           Int       @default(0)
  enrollments     Int       @default(0)
  completions     Int       @default(0)
  avgRating       Float?
  createdAt       DateTime  @default(now())
  @@unique([courseId, date])
  @@map("course_analytics")
}
'''

def schema_communications():
    return COMMON_HEADER + r'''
// COMMUNICATIONS SERVICE - Messages, Discussions, Replies

model MessageThread {
  id              String    @id @default(uuid())
  subject         String?
  participants    String[]
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("message_threads")
}

model ThreadMessage {
  id              String    @id @default(uuid())
  threadId        String
  senderId        String
  content         String    @db.Text
  attachments     String[]
  createdAt       DateTime  @default(now())
  @@index([threadId, senderId])
  @@map("thread_messages")
}

model Reply {
  id              String    @id @default(uuid())
  messageId       String
  senderId        String
  content         String    @db.Text
  createdAt       DateTime  @default(now())
  @@index([messageId])
  @@map("replies")
}
'''

def schema_search():
    return COMMON_HEADER + r'''
// SEARCH SERVICE - Index & Tracking metadata

model SearchIndex {
  id              String    @id @default(uuid())
  entityType      String
  entityId        String
  title           String
  content         String    @db.Text
  keywords        String[]
  language        String?
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([entityType, entityId])
  @@map("search_index")
}

model SearchTracking {
  id              String    @id @default(uuid())
  query           String
  resultCount     Int
  latencyMs       Int
  createdAt       DateTime  @default(now())
  @@map("search_tracking")
}
'''

def schema_storage():
    return COMMON_HEADER + r'''
// STORAGE SERVICE - File, Upload, MediaAsset, Quota, CDNCache, VideoProcessing

enum FileType {
  VIDEO
  IMAGE
  DOCUMENT
  AUDIO
  ARCHIVE
  CODE
  DATASET
  OTHER
}

enum StorageProvider {
  AWS_S3
  AZURE_BLOB
  GOOGLE_CLOUD
  LOCAL
  CLOUDINARY
}

enum ProcessingStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
}

model File {
  id              String          @id @default(uuid())
  userId          String
  filename        String
  originalName    String
  mimeType        String
  fileType        FileType
  fileSize        Int
  provider        StorageProvider
  storageKey      String          @unique
  bucket          String?
  url             String
  cdnUrl          String?
  width           Int?
  height          Int?
  duration        Int?
  status          ProcessingStatus @default(COMPLETED)
  thumbnailUrl    String?
  isPublic        Boolean         @default(false)
  downloadCount   Int             @default(0)
  viewCount       Int             @default(0)
  relatedEntity   String?
  relatedEntityId String?
  expiresAt       DateTime?
  uploadedAt      DateTime        @default(now())
  createdAt       DateTime        @default(now())
  updatedAt       DateTime        @updatedAt
  deletedAt       DateTime?
  @@index([userId, fileType])
  @@map("files")
}

model Upload {
  id              String          @id @default(uuid())
  userId          String
  sessionId       String          @unique
  filename        String
  fileSize        Int
  mimeType        String
  uploadId        String?
  parts           Json?
  bytesUploaded   Int             @default(0)
  progress        Float           @default(0)
  status          ProcessingStatus @default(PENDING)
  fileId          String?
  errorMessage    String?
  startedAt       DateTime        @default(now())
  completedAt     DateTime?
  expiresAt       DateTime?
  createdAt       DateTime      @default(now())
  @@index([userId, status])
  @@map("uploads")
}

model MediaAsset {
  id              String    @id @default(uuid())
  fileId          String    @unique
  originalUrl     String
  originalSize    Int
  thumbnailUrl    String?
  smallUrl        String?
  mediumUrl       String?
  largeUrl        String?
  videoFormats    Json?
  streamUrl       String?
  imageFormats    Json?
  isProcessed     Boolean   @default(false)
  processingStarted DateTime?
  processingCompleted DateTime?
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@index([fileId])
  @@map("media_assets")
}

def schema_storage_tail(): pass
'''

def schema_security():
    return COMMON_HEADER + r'''
// SECURITY SERVICE - SecurityEvents, BlockedIP, AuditLogs

enum SecuritySeverity {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

model SecurityEvent {
  id              String    @id @default(uuid())
  serviceName     String
  eventType       String
  severity        SecuritySeverity
  details         Json?
  ipAddress       String?
  userId          String?
  occurredAt      DateTime  @default(now())
  createdAt       DateTime  @default(now())
  @@index([serviceName, eventType, occurredAt])
  @@map("security_events")
}

model BlockedIP {
  id              String    @id @default(uuid())
  ipAddress       String    @unique
  reason          String?
  blockedUntil    DateTime?
  createdAt       DateTime  @default(now())
  @@map("blocked_ips")
}

model AuditLog {
  id              String    @id @default(uuid())
  actorId         String?
  action          String
  resourceType    String
  resourceId      String
  details         Json?
  createdAt       DateTime  @default(now())
  @@index([actorId, resourceType])
  @@map("audit_logs")
}
'''

def schema_monitoring():
    return COMMON_HEADER + r'''
// MONITORING SERVICE - ServiceHealth, Metrics, Alerts, Uptime, PerformanceLog, ErrorLog

enum ServiceStatus {
  HEALTHY
  DEGRADED
  DOWN
  MAINTENANCE
}

enum AlertSeverity {
  INFO
  WARNING
  ERROR
  CRITICAL
}

enum AlertStatus {
  OPEN
  ACKNOWLEDGED
  RESOLVED
  CLOSED
}

model ServiceHealth {
  id              String        @id @default(uuid())
  serviceName     String        @unique
  status          ServiceStatus @default(HEALTHY)
  avgResponseTime Float?
  p95ResponseTime Float?
  p99ResponseTime Float?
  uptime          Float?
  downtime        Int?
  requestCount    Int           @default(0)
  errorCount      Int           @default(0)
  cpuUsage        Float?
  memoryUsage     Float?
  diskUsage       Float?
  lastCheckAt     DateTime
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("service_health")
}

model Metric {
  id              String    @id @default(uuid())
  serviceName     String
  metricName      String
  value           Float
  unit            String?
  labels          Json?
  timestamp       DateTime  @default(now())
  @@index([serviceName, metricName, timestamp])
  @@map("metrics")
}

model Alert {
  id              String        @id @default(uuid())
  title           String
  description     String        @db.Text
  severity        AlertSeverity
  status          AlertStatus   @default(OPEN)
  serviceName     String?
  metricName      String?
  threshold       Float?
  actualValue     Float?
  triggeredAt     DateTime      @default(now())
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt
  @@map("alerts")
}

model PerformanceLog {
  id              String    @id @default(uuid())
  serviceName     String
  endpoint        String
  method          String
  statusCode      Int
  responseTime    Int
  userId          String?
  ipAddress       String?
  timestamp       DateTime  @default(now())
  @@index([serviceName, endpoint, timestamp])
  @@map("performance_logs")
}

model ErrorLog {
  id              String    @id @default(uuid())
  serviceName     String
  errorType       String
  errorMessage    String    @db.Text
  stackTrace      String?
  endpoint        String?
  method          String?
  userId          String?
  occurrences     Int       @default(1)
  firstSeenAt     DateTime  @default(now())
  lastSeenAt      DateTime  @default(now())
  isResolved      Boolean   @default(false)
  resolvedAt      DateTime?
  createdAt       DateTime  @default(now())
  @@map("error_logs")
}

model Uptime {
  id              String    @id @default(uuid())
  serviceName     String
  date            DateTime  @db.Date
  status          ServiceStatus
  uptimeSeconds   Int       @default(0)
  downtimeSeconds Int       @default(0)
  incidentCount   Int       @default(0)
  createdAt       DateTime  @default(now())
  @@unique([serviceName, date])
  @@map("uptime")
}
'''

def schema_ai_gateway():
    return COMMON_HEADER + r'''
// AI GATEWAY - Integrations, Models, Requests, Usage, Templates

model Integration {
  id              String    @id @default(uuid())
  name            String
  provider        String
  config          Json
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("ai_integrations")
}

model AIModel {
  id              String    @id @default(uuid())
  name            String
  provider        String
  capabilities    String[]
  config          Json?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("ai_models")
}

model AIRequest {
  id              String    @id @default(uuid())
  userId          String?
  modelId         String?
  prompt          String    @db.Text
  response        String?   @db.Text
  tokensUsed      Int?
  latencyMs       Int?
  createdAt       DateTime  @default(now())
  @@index([userId, createdAt])
  @@map("ai_requests")
}

model AIUsage {
  id              String    @id @default(uuid())
  date            DateTime  @db.Date
  modelId         String?
  requests        Int       @default(0)
  tokens          Int       @default(0)
  cost            Float?
  createdAt       DateTime  @default(now())
  @@unique([date, modelId])
  @@map("ai_usage")
}

model AITemplate {
  id              String    @id @default(uuid())
  name            String
  description     String?
  promptTemplate  String    @db.Text
  variables       String[]
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("ai_templates")
}
'''

def schema_i18n():
    return COMMON_HEADER + r'''
// I18N SERVICE - Languages, Translations, LocaleData

model Language {
  id              String    @id @default(uuid())
  code            String    @unique
  name            String
  nativeName      String?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("languages")
}

model Translation {
  id              String    @id @default(uuid())
  key             String
  languageCode    String
  value           String    @db.Text
  context         String?
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@unique([key, languageCode])
  @@map("translations")
}

model LocaleData {
  id              String    @id @default(uuid())
  languageCode    String
  timezone        String
  dateFormat      String
  numberFormat    String
  createdAt       DateTime  @default(now())
  @@map("locale_data")
}
'''

def schema_sponsors():
    return COMMON_HEADER + r'''
// SPONSORS SERVICE - Sponsors, Campaigns, Sponsorships, Ads

model Sponsor {
  id              String    @id @default(uuid())
  name            String
  website         String?
  logoUrl         String?
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("sponsors")
}

model Campaign {
  id              String    @id @default(uuid())
  sponsorId       String
  name            String
  startDate       DateTime
  endDate         DateTime
  budget          Float?
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("campaigns")
}

model Sponsorship {
  id              String    @id @default(uuid())
  sponsorId       String
  entityType      String
  entityId        String
  startDate       DateTime
  endDate         DateTime
  createdAt       DateTime  @default(now())
  @@map("sponsorships")
}

model Ad {
  id              String    @id @default(uuid())
  campaignId      String
  creativeUrl     String
  destinationUrl  String
  isActive        Boolean   @default(true)
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@map("ads")
}
'''

def schema_enrollment():
    return COMMON_HEADER + r'''
// ENROLLMENT SERVICE - Enrollment, Progress, Certificate, Notes, Bookmarks, StudySession

enum EnrollmentStatus {
  ACTIVE
  COMPLETED
  SUSPENDED
  EXPIRED
  CANCELLED
  IN_PROGRESS
  PAUSED
}

model Enrollment {
  id                  String           @id @default(uuid())
  studentId           String
  courseId            String
  status              EnrollmentStatus @default(ACTIVE)
  progress            Float            @default(0)
  isCompleted         Boolean          @default(false)
  completedAt         DateTime?
  certificateIssued   Boolean          @default(false)
  certificateId       String?
  totalTimeSpent      Int              @default(0)
  lastAccessedAt      DateTime?
  purchasePrice       Float?
  paymentId           String?
  enrolledAt          DateTime         @default(now())
  expiresAt           DateTime?
  createdAt           DateTime         @default(now())
  updatedAt           DateTime         @updatedAt
  @@unique([studentId, courseId])
  @@index([studentId, status])
  @@map("enrollments")
}

model Progress {
  id              String    @id @default(uuid())
  studentId       String
  lessonId        String
  courseId        String
  isCompleted     Boolean   @default(false)
  percentage      Float     @default(0)
  timeSpent       Int       @default(0)
  lastPosition    Int?
  watchedDuration Int       @default(0)
  quizScore       Float?
  quizAttempts    Int       @default(0)
  notesCount      Int       @default(0)
  questionsAsked  Int       @default(0)
  completedAt     DateTime?
  firstAccessedAt DateTime  @default(now())
  lastAccessedAt  DateTime  @default(now())
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@unique([studentId, lessonId])
  @@map("progress")
}

model Certificate {
  id              String    @id @default(uuid())
  studentId       String
  courseId        String
  enrollmentId    String
  certificateNumber String  @unique
  verificationCode String  @unique
  studentName     String
  studentEmail    String
  courseTitle     String
  completionDate  DateTime
  issueDate       DateTime  @default(now())
  score           Float?
  grade           String?
  certificateUrl  String
  isValid         Boolean   @default(true)
  revokedAt       DateTime?
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  @@unique([studentId, courseId])
  @@map("certificates")
}
'''
    
def schema_reviews():
    return COMMON_HEADER + r''' 
// REVIEWS SERVICE - Review, Rating, Report, Analytics

enum ReviewStatus {
  PENDING
  APPROVED
  REJECTED
  FLAGGED
}

model Review {
  id              String        @id @default(uuid())
  courseId        String
  studentId       String
  rating          Float
  comment         String?       @db.Text
  status          ReviewStatus  @default(APPROVED)
  isFeatured      Boolean       @default(false)
  likes           Int           @default(0)
  dislikes        Int           @default(0)
  reportedCount   Int           @default(0)
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt
  @@unique([courseId, studentId])
  @@index([courseId, status])
  @@map("reviews")
}

model ReviewReport {
  id              String    @id @default(uuid())
  reviewId        String
  reportedBy      String
  reason          String
  details         String?   @db.Text
  resolved        Boolean   @default(false)
  resolvedAt      DateTime?
  createdAt       DateTime  @default(now())
  @@index([reviewId, resolved])
  @@map("review_reports")
}

model RatingAnalytics {
  id              String    @id @default(uuid())
  courseId        String
  averageRating   Float     @default(0)
  totalReviews    Int       @default(0)
  fiveStars       Int       @default(0)
  fourStars       Int       @default(0)
  threeStars      Int       @default(0)
  twoStars        Int       @default(0)
  oneStar         Int       @default(0)
  updatedAt       DateTime  @default(now())
  @@unique([courseId])
  @@map("rating_analytics")
}
'''

def schema_default(name):
    """Fallback schema si un service inconnu est trouvé."""
    return COMMON_HEADER + f'''
// DEFAULT PLACEHOLDER for {name.upper()}

model Example {{
  id        String   @id @default(uuid())
  name      String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}}
'''

# =========================
# MAPPAGE DES SCHÉMAS
# =========================
SCHEMA_MAP = {
    'auth-service': schema_auth,
    'user-service': schema_user,
    'courses-service': schema_courses,
    'quizzes-service': schema_quizzes,
    'bookings-service': schema_bookings,
    'payments-service': schema_payments,
    'notifications-service': schema_notifications,
    'webinars-service': schema_webinars,
    'gamification-service': schema_gamification,
    'chatbot-service': schema_chatbot,
    'analytics-service': schema_analytics,
    'communications-service': schema_communications,
    'search-service': schema_search,
    'storage-service': schema_storage,
    'security-service': schema_security,
    'monitoring-service': schema_monitoring,
    'ai-gateway': schema_ai_gateway,
    'i18n-service': schema_i18n,
    'sponsors-service': schema_sponsors,
    'enrollment-service': schema_enrollment,
    'reviews-service': schema_reviews,
}

# =========================
# CLASSE PRINCIPALE
# =========================
class PrismaSchemaUpdater:
    def __init__(self, base_dir="."):
        self.base = Path(base_dir).resolve()

    def run(self):
        print("🔍 Vérification et mise à jour des schémas Prisma dans :")
        print(f"📂 {self.base}\n")

        created, updated, skipped = [], [], []

        for service, cfg in MICROSERVICES.items():
            if cfg.get("no_prisma"):
                print(f"⏭️  {service} (pas de Prisma)")
                continue

            prisma_dir = self.base / "microservices" / service / "prisma"
            schema_file = prisma_dir / "schema.prisma"

            prisma_dir.mkdir(parents=True, exist_ok=True)

            generator_func = SCHEMA_MAP.get(service, lambda: schema_default(service))
            schema_content = generator_func()

            if not schema_file.exists():
                schema_file.write_text(schema_content, encoding="utf-8")
                print(f"🆕 Créé → {schema_file}")
                created.append(service)
                continue

            # Vérifier si placeholder ou contenu vide
            content = schema_file.read_text(encoding="utf-8").strip()
            if not content or "model Example" in content or "DEFAULT PRISMA SCHEMA" in content:
                schema_file.write_text(schema_content, encoding="utf-8")
                print(f"♻️ Remplacé (placeholder détecté) → {schema_file}")
                updated.append(service)
            else:
                print(f"✅ Déjà complet → {schema_file}")
                skipped.append(service)

        print("\n===================== RÉSUMÉ =====================")
        print(f"🆕 Fichiers créés       : {len(created)}")
        if created:
            print("   → " + ", ".join(created))
        print(f"♻️ Fichiers mis à jour  : {len(updated)}")
        if updated:
            print("   → " + ", ".join(updated))
        print(f"✅ Fichiers inchangés   : {len(skipped)}")
        if skipped:
            print("   → " + ", ".join(skipped))
        print("===================================================")
        print("🎯 Tous les schémas sont maintenant complets et à jour.")

# =========================
# EXÉCUTION
# =========================
if __name__ == "__main__":
    PrismaSchemaUpdater().run()
