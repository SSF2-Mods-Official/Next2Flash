package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmash_111 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var attackBox4:MovieClip;
        public var camBox:MovieClip;
        public var self:gameandwatchExt;
        public var loop:*;
        public var timer:*;
        public var anim:String;
        public var originalGrav:Number;
        public var hasJumped:Boolean;
        public var hasDJed:Boolean;
        public var currentSound:Number;
        public var currentSound2:Number;
        public var jumpSpeed:*;
        public var finalSmashBar:FinalSmashBar;
        public var maxRiseSpeed:*;
        public var riseAccel:*;
        public var newSpeed:*;

        public function FinalSmash_111()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 23, this.frame24, 24, this.frame25, 25, this.frame26, 34, this.frame35, 35, this.frame36, 39, this.frame40, 41, this.frame42, 43, this.frame44, 77, this.frame78, 78, this.frame79, 102, this.frame103, 103, this.frame104);
        }

        public function setupBar():*
        {
            this.finalSmashBar = new FinalSmashBar(this.timer);
            this.finalSmashBar.addToDamageMeter(this.self.getHealthBox());
            this.self.setFinalSmashMeterCharge(0);
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.clearBar, {"persistent":true});
        }

        public function clearBar(_arg_1:*=null):*
        {
            this.finalSmashBar.removeFromDamageMeter(this.self.getHealthBox());
            this.finalSmashBar = null;
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.clearBar);
        }

        public function processInputs():*
        {
            var _local_1:* = this.self.getControls(true);
            if (this.self.isOnGround())
            {
                this.hasJumped = false;
                this.hasDJed = false;
            }
            else
            {
                this.hasJumped = true;
            };
            this.timer--;
            if (this.timer < 60)
            {
                if ((this.timer % 2) == 1)
                {
                    this.self.setVisibility(false);
                }
                else
                {
                    this.self.setVisibility(true);
                };
            };
            if (this.finalSmashBar != null)
            {
                this.finalSmashBar.updateBar(this.timer);
            };
            if (this.timer < 0)
            {
                this.self.destroyTimer(this.processInputs);
                this.self.setVisibility(true);
                this.self.stancePlayFrame("outro");
            };
            if (_local_1.JUMP)
            {
                if (!this.hasJumped)
                {
                    this.self.setYSpeed(this.jumpSpeed);
                    this.hasJumped = true;
                    this.hasDJed = false;
                }
                else if (!this.hasDJed)
                {
                    this.self.setYSpeed(this.jumpSpeed);
                    this.hasDJed = true;
                };
            };
            if (_local_1.BUTTON1 || (_local_1.BUTTON2 && (this.anim == "idle")))
            {
                this.self.stancePlayFrame("attack");
            };
        }

        public function loopSound(_arg_1:*=null):*
        {
            this.currentSound = this.self.playSound("fs_ambient_1");
            this.self.createTimer(26, 0, this.loopSound2);
        }

        public function loopSound2(_arg_1:*=null):*
        {
            this.currentSound2 = this.self.playSound("fs_ambient_2");
            this.self.destroyTimer(this.loopSound2);
        }

        public function stopAmbience(_arg_1:*=null):*
        {
            this.self.setVisibility(true);
            this.self.destroyTimer(this.loopSound);
            this.self.destroyTimer(this.loopSound2);
            this.self.stopSound(this.currentSound);
            this.self.stopSound(this.currentSound2);
        }

        public function rise():*
        {
            var _local_1:* = this.self.getControls();
            if (_local_1.JUMP || _local_1.UP)
            {
                this.newSpeed = (this.self.getYSpeed() + this.riseAccel);
                if (this.newSpeed < this.maxRiseSpeed)
                {
                    this.newSpeed = this.maxRiseSpeed;
                };
                this.self.setYSpeed(this.newSpeed);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            this.loop = false;
            this.timer = 450;
            this.anim = "intro";
            this.hasJumped = false;
            this.hasDJed = false;
            this.currentSound = 0;
            this.currentSound2 = 0;
            this.jumpSpeed = -19;
            if (SSF2API.isReady() && parent)
            {
                this.originalGrav = this.self.getCharacterStat("gravity");
                this.self.setMetalStatus(false);
                this.self.setCamBoxSize(200, 100);
                this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.stopAmbience);
                this.self.unnattachFromGround();
            };
        }

        internal function frame6():*
        {
            this.self.playSound("fs_start");
        }

        internal function frame24():*
        {
            this.maxRiseSpeed = -10;
            this.riseAccel = -2;
            this.newSpeed = 0;
        }

        internal function frame25():*
        {
            this.setupBar();
            this.self.createTimer(1, -1, this.processInputs);
            this.self.createTimer(1, 1, this.loopSound);
            this.self.createTimer(52, 0, this.loopSound);
        }

        internal function frame26():*
        {
            this.anim = "idle";
            this.self.updateAttackStats({"air_ease":5});
        }

        internal function frame35():*
        {
            this.self.stancePlayFrame("idle");
        }

        internal function frame36():*
        {
            this.anim = "attack";
        }

        internal function frame40():*
        {
            this.self.playSound("gw_jabpull");
        }

        internal function frame42():*
        {
            this.self.playSound("gw_nairend");
        }

        internal function frame44():*
        {
            this.self.playSound("gw_aerial1");
        }

        internal function frame78():*
        {
            this.self.stancePlayFrame("idle");
        }

        internal function frame79():*
        {
            this.anim = "outro";
            this.self.updateAttackStats({
                "air_ease":0,
                "allowControl":false,
                "allowControlGround":false
            });
            this.self.setXSpeed(0);
            this.stopAmbience();
            this.self.playSound("fs_end");
            this.clearBar();
            this.self.destroyTimer(this.rise);
        }

        internal function frame103():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({
                    "allowControl":true,
                    "allowControlGround":true
                });
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame104():*
        {
            this.self.endAttack();
        }


    }
}

