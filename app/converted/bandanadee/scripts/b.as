package
{
    import flash.display.MovieClip;

    public dynamic class b extends MovieClip
    {

        public var attackBox:MovieClip;
        public var customBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var opponent:*;
        public var hurt:*;
        public var stuck:*;
        public var holdTime:*;
        public var frameCount:*;
        public var isChibi:*;
        public var timer:*;

        public function b()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 6, this.frame7, 8, this.frame9, 10, this.frame11, 11, this.frame12, 13, this.frame14, 15, this.frame16, 17, this.frame18, 18, this.frame19, 19, this.frame20);
        }

        public function countFrames():void
        {
            this.frameCount++;
        }

        public function groundListen(_arg_1:*=null):void
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundListen);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.groundListen);
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.updateProjectileStats({
                "maxgravity":0,
                "gravity":0,
                "rotate":false
            });
            this.stuck = true;
            this.self.stancePlayFrame("continue");
        }

        public function pinDown(_arg_1:*=null):void
        {
            if (this.stuck)
            {
                this.opponent = _arg_1.data.receiver;
                this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.pinDown);
                this.opponent.resetKnockback();
                this.self.stancePlayFrame("continueGrabbed");
            };
        }

        public function releaseFoe(_arg_1:*=null):void
        {
            this.opponent.removeEventListener(SSF2Event.CHAR_HURT, this.releaseFoe);
            this.opponent.removeEventListener(SSF2Event.CHAR_GRABBED, this.releaseFoe);
            this.self.removeEventListener(SSF2Event.PROJ_DESTROYED, this.releaseFoeTimeout);
            this.self.destroyTimer(this.hold);
            if (!this.hurt)
            {
                this.opponent.grabRelease();
            };
            this.self.destroy();
        }

        public function releaseFoeTimeout(_arg_1:*=null):void
        {
            this.hurt = false;
            this.releaseFoe();
        }

        public function hold():void
        {
            if (this.opponent != null)
            {
                this.opponent.forceHitStun(3);
                this.opponent.setX((this.self.getX() + this.self.flipX(10)));
                this.opponent.setY((this.self.getY() + 5));
                this.opponent.resetMovement();
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.opponent = null;
            this.hurt = true;
            this.stuck = false;
            this.holdTime = 20;
            this.frameCount = 0;
            if (this.self && SSF2API.isReady())
            {
                this.isChibi = (this.self.getOwner().getCharacterStat("statsName") == "chibirobo");
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.groundListen);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.groundListen);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.pinDown);
                this.self.createTimer(1, -1, this.countFrames);
                if (!this.isChibi)
                {
                    this.self.getOwner().spearObj = this.self;
                };
            };
        }

        internal function frame6():*
        {
            this.self.stancePlayFrame("thrown");
        }

        internal function frame7():*
        {
            this.self.updateAttackBoxStats(1, {
                "hitStun":0,
                "selfHitStun":0
            });
            this.self.refreshAttackID();
            this.self.attachEffect("global_dust_cloud");
            this.self.playSound("bandanadee_fspecEnd");
        }

        internal function frame9():*
        {
            if (!this.isChibi)
            {
                this.self.getOwner().spearObj = null;
            };
            this.timer = 20;
        }

        internal function frame11():*
        {
            if (this.timer <= 0)
            {
                this.self.destroy();
            }
            else
            {
                this.timer--;
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame12():*
        {
            if (this.opponent.getType() == "SSF2Character")
            {
                this.holdTime = (Math.floor((((1 + this.opponent.getDamage()) / 100) * 15)) + 17);
                this.self.destroyTimer(this.countFrames);
                this.self.updateProjectileStats({"time_max":(this.frameCount + this.holdTime)});
            };
        }

        internal function frame14():*
        {
            if (this.opponent.getType() == "SSF2Character")
            {
                this.opponent.setX((this.self.getX() + this.self.flipX(10)));
                this.opponent.setY((this.self.getY() + 5));
                this.opponent.setState(CState.INJURED);
                this.self.createTimer(1, 0, this.hold);
                this.opponent.addEventListener(SSF2Event.CHAR_HURT, this.releaseFoe, {"persistent":true});
                this.opponent.addEventListener(SSF2Event.CHAR_GRABBED, this.releaseFoe, {"persistent":true});
                this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.releaseFoeTimeout, {"persistent":true});
            };
        }

        internal function frame16():*
        {
            this.self.stancePlayFrame("loop2");
        }

        internal function frame18():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame19():*
        {
            this.self = SSF2API.getProjectile(this);
            this.opponent = null;
            this.hurt = true;
            this.stuck = false;
            this.holdTime = 20;
            this.frameCount = 0;
            if (this.self && SSF2API.isReady())
            {
                this.isChibi = true;
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.groundListen);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.groundListen);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.pinDown);
                this.self.createTimer(1, -1, this.countFrames);
            };
        }

        internal function frame20():*
        {
            this.self.stancePlayFrame("thrown");
        }


    }
}

