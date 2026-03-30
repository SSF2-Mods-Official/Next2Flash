package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_specialS_58 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var timer:*;
        public var controls:*;
        public var canCancel:Boolean;
        public var cancel:Boolean;
        public var short:Boolean;

        public function fox_specialS_58()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 16, this.frame17, 19, this.frame20, 21, this.frame22, 22, this.frame23, 30, this.frame31, 31, this.frame32, 33, this.frame34, 40, this.frame41, 42, this.frame43, 44, this.frame45, 50, this.frame51, 53, this.frame54, 59, this.frame60);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function setPos():void
        {
            this.self.setGlobalVariable(("dashX" + this.timer), this.self.getX());
            this.self.setGlobalVariable(("dashY" + this.timer), this.self.getY());
            this.timer++;
            this.self.setGlobalVariable("dashLim", this.timer);
        }

        public function moveIt():void
        {
            this.self.setXSpeed(50, false);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            this.timer = 0;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.playAttackSound(1);
                this.self.attachEffect("global_spark", {
                    "x":this.flipX(25),
                    "y":-29
                });
                this.self.attachEffect("global_dust_heavy", {"x":this.flipX(27)});
            };
        }

        internal function frame2():*
        {
            this.controls = this.self.getControls();
            this.canCancel = true;
            this.cancel = false;
        }

        internal function frame5():*
        {
            this.controls = this.self.getControls();
            if (this.controls.BUTTON1)
            {
                this.canCancel = false;
            };
        }

        internal function frame6():*
        {
            this.controls = this.self.getControls();
            if (this.controls.BUTTON1)
            {
                this.canCancel = false;
            };
        }

        internal function frame7():*
        {
            this.controls = this.self.getControls();
            if (this.controls.BUTTON1 && this.canCancel)
            {
                this.cancel = true;
            };
        }

        internal function frame8():*
        {
            this.controls = this.self.getControls();
            if (this.controls.BUTTON1 && this.canCancel)
            {
                this.cancel = true;
            };
        }

        internal function frame9():*
        {
            this.controls = this.self.getControls();
            if (this.controls.BUTTON1 && this.canCancel)
            {
                this.cancel = true;
            };
        }

        internal function frame10():*
        {
            this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
            this.controls = this.self.getControls();
            if ((this.controls.BUTTON1 || this.cancel) && this.canCancel)
            {
                this.self.stancePlayFrame("cancelled");
            };
            this.setPos();
            this.self.createTimer(1, 4, this.moveIt);
            this.self.createTimer(1, -1, this.setPos);
            this.self.attachEffect("global_dust_heavy", {"scaleY":0.5});
            this.self.applyPalette(this.self.attachEffect("fox_illusionblur"));
        }

        internal function frame11():*
        {
            this.self.fireProjectile("fox_fspecProj");
        }

        internal function frame12():*
        {
            this.self.applyPalette(this.self.attachEffect("fox_illusionblur"));
        }

        internal function frame13():*
        {
            this.self.fireProjectile("fox_fspecProj");
        }

        internal function frame14():*
        {
            this.self.setXSpeed(11, false);
            this.self.applyPalette(this.self.attachEffect("fox_illusionblur"));
        }

        internal function frame17():*
        {
            this.self.updateAttackBoxStats(1, {"damage":3});
        }

        internal function frame20():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "canFallOff":true,
                "xSpeedDecay":-0.1,
                "xSpeedDecayAir":-0.8
            });
            this.self.destroyTimer(this.setPos);
        }

        internal function frame22():*
        {
            var _local_1:* = __activation__;
            this.self.updateAttackStats({"xSpeedDecay":0});
            if (this.self.isOnGround())
            {
                this.self.updateAttackStats({"cancelWhenAirborne":true});
            }
            else
            {
                this.self.createTimer(1, 10, function ():*
                {
                    if (self.isOnGround())
                    {
                        self.updateAttackStats({"cancelWhenAirborne":true});
                    };
                });
            };
        }

        internal function frame23():*
        {
            if (!this.self.isOnGround())
            {
                this.self.stancePlayFrame("endAir");
            };
        }

        internal function frame31():*
        {
            this.self.toHelpless();
        }

        internal function frame32():*
        {
            this.short = true;
            this.self.destroyTimer(this.moveIt);
            this.self.destroyTimer(this.setPos);
        }

        internal function frame34():*
        {
            this.self.updateAttackStats({
                "xSpeedDecay":0,
                "xSpeedDecayAir":0
            });
            this.self.setXSpeed(11, false);
        }

        internal function frame41():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "xSpeedDecay":0,
                "xSpeedDecayAir":-0.5
            });
            if (this.self.isOnGround())
            {
                this.self.updateAttackStats({"cancelWhenAirborne":true});
            };
        }

        internal function frame43():*
        {
            if (!this.self.isOnGround())
            {
                this.self.stancePlayFrame("endAir");
            };
        }

        internal function frame45():*
        {
            if (this.self.isOnGround())
            {
                this.self.toHeavyLand();
            };
        }

        internal function frame51():*
        {
            this.self.toHelpless();
        }

        internal function frame54():*
        {
            if (this.short && this.self.isOnGround())
            {
                this.self.toHeavyLand();
            };
        }

        internal function frame60():*
        {
            if (this.self.isOnGround())
            {
                this.self.endAttack();
            }
            else
            {
                this.self.setGlobalVariable("usedUpB", true);
                this.self.toHelpless();
            };
        }


    }
}

