package kirby_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class LloydKirby_252 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var noPress:Boolean;
        public var doubleFang:Boolean;
        public var curFrame:int;

        public function LloydKirby_252()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 8, this.frame9, 18, this.frame19, 26, this.frame27, 28, this.frame29, 29, this.frame30, 34, this.frame35, 36, this.frame37, 38, this.frame39, 42, this.frame43);
        }

        public function disableNeutralB():void
        {
            this.self.setAttackEnabled(false, "b");
            this.self.setAttackEnabled(false, "b_air");
            this.self.createTimer(12, 1, this.enableNeutralB, {"persistent":true});
        }

        public function enableNeutralB():void
        {
            this.self.setAttackEnabled(true, "b");
            this.self.setAttackEnabled(true, "b_air");
        }

        public function doubleFangCheck():void
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.noPress = true;
            }
            else if (this.noPress)
            {
                this.doubleFang = true;
                this.self.destroyTimer(this.doubleFangCheck);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (SSF2API.isReady() && this.self)
            {
                this.controls = null;
                this.noPress = false;
                this.doubleFang = this.self.getGlobalVariable("KirbyLloydNSpecDubs");
                this.curFrame = this.self.getGlobalVariable("KirbyLloydNSpecFrame");
                this.self.setGlobalVariable("KirbyLloydNSpecDubs", false);
                this.self.setGlobalVariable("KirbyLloydNSpecFrame", 0);
                if ((this.curFrame < 8) && !(this.doubleFang))
                {
                    this.self.createTimer(1, -1, this.doubleFangCheck);
                };
                if (this.curFrame > 1)
                {
                    this.noPress = true;
                    this.self.stancePlayFrame(this.curFrame);
                };
            };
        }

        internal function frame7():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(5), 0);
            };
        }

        internal function frame8():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(7)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(7)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(3.5), 0);
            };
            this.self.destroyTimer(this.doubleFangCheck);
            if (this.curFrame != currentFrame)
            {
                this.self.playAttackSound(2);
                if (!this.doubleFang)
                {
                    this.self.playVoiceSound(1);
                }
                else
                {
                    this.self.playVoiceSound(2);
                };
            };
        }

        internal function frame9():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(2), 0);
            };
            if (this.curFrame != currentFrame)
            {
                this.self.fireProjectile("demonfang");
                this.self.attachEffect("global_dust_heavy", {
                    "x":this.self.flipX(5),
                    "y":3,
                    "scaleX":-0.5,
                    "scaleY":-0.5
                });
                SSF2API.getCamera().shake(2);
                if (this.doubleFang)
                {
                    this.self.stancePlayFrame("attack2");
                };
            };
        }

        internal function frame19():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }

        internal function frame27():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame29():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playAttackSound(2);
            };
        }

        internal function frame30():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.fireProjectile("demonfang");
                this.self.attachEffect("global_dust_heavy", {
                    "x":this.self.flipX(5),
                    "y":3,
                    "scaleX":-0.5,
                    "scaleY":-0.5
                });
                SSF2API.getCamera().shake(2);
            };
        }

        internal function frame35():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(10), 0);
            };
        }

        internal function frame37():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(7)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(7)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(7), 0);
            };
        }

        internal function frame39():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(4)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(4), 0);
            };
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("lloyd_footstep");
            };
        }

        internal function frame43():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }


    }
}

