package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class USpecial_32 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var startedSwinging:Boolean;
        public var arcRadius:*;
        public var initialJump:Number;
        public var swingJumpSpeedY:Number;
        public var swingJumpSpeedX:Number;
        public var projectile:*;

        public function USpecial_32()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 6, this.frame7, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 16, this.frame17, 17, this.frame18, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 22, this.frame23, 23, this.frame24, 34, this.frame35, 56, this.frame57);
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
                    this.self.setYSpeed(0);
                    this.self.setXSpeed(0);
                }
                else
                {
                    this.self.setYSpeed(-15);
                    this.self.setXSpeed(-5, false);
                };
                this.self.stancePlayFrame("bounce");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.startedSwinging = false;
            this.arcRadius = 109;
            this.initialJump = -20;
            this.swingJumpSpeedY = -15;
            this.swingJumpSpeedX = 9;
            if (SSF2API.isReady() && parent)
            {
                this.self.resetKnockback();
                this.self.setGlobalVariable("tether", true);
                this.self.setYSpeed(this.initialJump);
                this.self.setXSpeed(0);
                this.self.fireProjectile("batSwingRing", 102, -150);
                this.projectile = this.self.getCurrentProjectile();
            };
        }

        internal function frame2():*
        {
            this.self.addEventListener(SSF2Event.HIT_WALL, this.wallHit);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.swingLand);
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
            this.self.endAttack();
        }

        internal function frame57():*
        {
            this.self.endAttack();
        }


    }
}

