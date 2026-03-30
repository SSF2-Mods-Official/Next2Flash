package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class USpecialAir_33 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hand:MovieClip;
        public var hand2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var batSwing:Boolean;
        public var startedSwinging:Boolean;
        public var properGravity:Number;
        public var arcRadius:*;
        public var initialJump:Number;
        public var swingJumpSpeedY:Number;
        public var swingJumpSpeedX:Number;
        public var swinglessHit:*;

        public function USpecialAir_33()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 6, this.frame7, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 16, this.frame17, 17, this.frame18, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 22, this.frame23, 23, this.frame24, 34, this.frame35, 39, this.frame40, 56, this.frame57, 63, this.frame64, 65, this.frame66, 67, this.frame68, 75, this.frame76);
        }

        public function swingLand(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.wallHit);
            this.self.toHeavyLand();
        }

        public function wallHit(_arg_1:*=null):*
        {
            if (currentFrame >= 12)
            {
                this.self.updateAttackStats({"air_ease":-1});
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.swingLand);
                this.self.removeEventListener(SSF2Event.HIT_WALL, this.wallHit);
                if (_arg_1.data.top && !(_arg_1.data.left || _arg_1.data.right))
                {
                    this.self.setGlobalVariable("canSwing", false);
                    this.self.setYSpeed(0);
                    this.self.setXSpeed(0);
                }
                else
                {
                    this.self.setYSpeed(Math.min((-15 + this.self.getGlobalVariable("upBBounces")), 0));
                    this.self.setXSpeed(-5, false);
                };
                this.self.stancePlayFrame("bounce");
            };
        }

        public function resetSwing(_arg_1:*=null):*
        {
            this.self.setGlobalVariable("canSwing", true);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.startedSwinging = false;
            this.arcRadius = 109;
            this.initialJump = -15;
            this.swingJumpSpeedY = -15;
            this.swingJumpSpeedX = 9;
            if (SSF2API.isReady() && parent)
            {
                this.self.resetKnockback();
                this.self.setGlobalVariable("tether", true);
                this.self.setYSpeed(this.initialJump);
                if (!this.self.getGlobalVariable("canSwing"))
                {
                    this.self.stancePlayFrame("fail");
                    this.self.updateAttackStats({"xSpeedDecay":0});
                }
                else
                {
                    this.self.setXSpeed(0);
                    this.self.fireProjectile("batSwingRing", 100, -100);
                    this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.swingLand);
                    this.self.addEventListener(SSF2Event.STATE_CHANGE, this.resetSwing);
                };
            };
            this.swinglessHit = {
                "damage":10,
                "power":30,
                "kbConstant":80,
                "direction":70
            };
        }

        internal function frame2():*
        {
            this.self.addEventListener(SSF2Event.HIT_WALL, this.wallHit);
        }

        internal function frame7():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame11():*
        {
            this.self.setGlobalVariable("tether", false);
        }

        internal function frame12():*
        {
            this.self.updateAttackStats({"air_ease":(0.26 * this.arcRadius)});
            this.self.setXSpeed((0.03 * this.arcRadius), false);
            this.self.setYSpeed((0.26 * this.arcRadius));
        }

        internal function frame13():*
        {
            this.self.updateAttackStats({"air_ease":(0.24 * this.arcRadius)});
            this.self.setXSpeed((0.1 * this.arcRadius), false);
            this.self.setYSpeed((0.24 * this.arcRadius));
        }

        internal function frame14():*
        {
            this.self.updateAttackStats({"air_ease":(0.21 * this.arcRadius)});
            this.self.setXSpeed((0.16 * this.arcRadius), false);
            this.self.setYSpeed((0.21 * this.arcRadius));
        }

        internal function frame15():*
        {
            this.self.updateAttackStats({"air_ease":(0.16 * this.arcRadius)});
            this.self.setXSpeed((0.21 * this.arcRadius), false);
            this.self.setYSpeed((0.16 * this.arcRadius));
        }

        internal function frame16():*
        {
            this.self.updateAttackStats({"air_ease":(0.1 * this.arcRadius)});
            this.self.setXSpeed((0.24 * this.arcRadius), false);
            this.self.setYSpeed((0.1 * this.arcRadius));
            this.self.playAttackSound(2);
        }

        internal function frame17():*
        {
            this.self.updateAttackStats({"air_ease":(0.03 * this.arcRadius)});
            this.self.setXSpeed((0.26 * this.arcRadius), false);
            this.self.setYSpeed((0.03 * this.arcRadius));
        }

        internal function frame18():*
        {
            this.self.updateAttackStats({"air_ease":0});
            this.self.setXSpeed((0.26 * this.arcRadius), false);
            this.self.setYSpeed((-0.03 * this.arcRadius));
        }

        internal function frame19():*
        {
            this.self.setXSpeed((0.24 * this.arcRadius), false);
            this.self.setYSpeed((-0.1 * this.arcRadius));
        }

        internal function frame20():*
        {
            this.self.setXSpeed((0.21 * this.arcRadius), false);
            this.self.setYSpeed((-0.16 * this.arcRadius));
        }

        internal function frame21():*
        {
            this.self.setXSpeed((0.16 * this.arcRadius), false);
            this.self.setYSpeed((-0.21 * this.arcRadius));
        }

        internal function frame22():*
        {
            this.self.setXSpeed((0.1 * this.arcRadius), false);
            this.self.setYSpeed((-0.24 * this.arcRadius));
        }

        internal function frame23():*
        {
            this.self.setXSpeed((0.03 * this.arcRadius), false);
            this.self.setYSpeed((-0.26 * this.arcRadius));
        }

        internal function frame24():*
        {
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.wallHit);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.swingLand);
            this.self.setXSpeed(this.swingJumpSpeedX, false);
            this.self.setYSpeed(this.swingJumpSpeedY);
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame35():*
        {
            this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.resetSwing);
            this.self.setGlobalVariable("canSwing", false);
            this.self.endAttack();
        }

        internal function frame40():*
        {
            this.self.setGlobalVariable("upBBounces", (this.self.getGlobalVariable("upBBounces") + 1));
        }

        internal function frame57():*
        {
            this.self.endAttack();
        }

        internal function frame64():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame66():*
        {
            this.self.updateAttackBoxStats(1, this.swinglessHit);
            this.self.updateAttackBoxStats(2, this.swinglessHit);
        }

        internal function frame68():*
        {
            this.self.setGlobalVariable("tether", false);
        }

        internal function frame76():*
        {
            this.self.toHelpless();
        }


    }
}

