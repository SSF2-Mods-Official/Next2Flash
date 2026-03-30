package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class NeutralSpecial_Ground__40 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var redirectBlaster:*;
        public var projectile:*;
        public var hasntFired:*;
        public var playsound:*;
        public var xframe:*;
        public var controls:Object;
        public var localBlaster:*;

        public function NeutralSpecial_Ground__40()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 29, this.frame30, 30, this.frame31, 38, this.frame39);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function testButton():void
        {
            this.controls = this.self.getControls();
            this.localBlaster = this.self.getGlobalVariable("blasterAngle");
            if (this.controls.BUTTON1 || this.hasntFired)
            {
                if (this.controls.UP && (this.localBlaster < 90))
                {
                    this.localBlaster += 10;
                }
                else if (this.controls.DOWN && (this.localBlaster > 0))
                {
                    this.localBlaster -= 10;
                };
                this.self.setGlobalVariable("blasterAngle", this.localBlaster);
                if (this.currentLabel != "fire")
                {
                    this.redirectBlaster = ("degree" + this.localBlaster);
                    this.self.stancePlayFrame(this.redirectBlaster);
                };
            }
            else if (this.currentLabel != "fire")
            {
                this.self.destroyTimer(this.testButton);
                this.self.destroyTimer(this.fire);
                this.self.endAttack();
            };
        }

        public function fire():void
        {
            this.self.stancePlayFrame("fire");
            this.hasntFired = false;
            if (this.localBlaster == 0)
            {
                this.self.fireProjectile("chibi_blaster", -8, 4);
            }
            else if (this.localBlaster == 10)
            {
                this.self.fireProjectile("chibi_blaster", -10, 2);
            }
            else if (this.localBlaster == 20)
            {
                this.self.fireProjectile("chibi_blaster", -12, 0);
            }
            else if (this.localBlaster == 30)
            {
                this.self.fireProjectile("chibi_blaster", -14, -2);
            }
            else if (this.localBlaster == 40)
            {
                this.self.fireProjectile("chibi_blaster", -16, -4);
            }
            else if (this.localBlaster == 50)
            {
                this.self.fireProjectile("chibi_blaster", -18, -6);
            }
            else if (this.localBlaster == 60)
            {
                this.self.fireProjectile("chibi_blaster", -20, -8);
            }
            else if (this.localBlaster == 70)
            {
                this.self.fireProjectile("chibi_blaster", -22, -10);
            }
            else if (this.localBlaster == 80)
            {
                this.self.fireProjectile("chibi_blaster", -24, -12);
            }
            else if (this.localBlaster == 90)
            {
                this.self.fireProjectile("chibi_blaster", -28, -14);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.hasntFired = true;
            this.xframe = "startup";
            if (parent && this.self && SSF2API.isReady())
            {
                this.controls = this.self.getControls();
                this.self.setGlobalVariable("blasterAngle", 0);
                this.localBlaster = this.self.getGlobalVariable("blasterAngle");
                if (this.localBlaster == null)
                {
                    this.localBlaster = 0;
                };
                this.self.attachEffect("global_spark", {
                    "x":this.flipX(23),
                    "y":-30
                });
            };
        }

        internal function frame6():*
        {
            this.self.createTimer(1, 0, this.testButton);
            this.self.createTimer(10, 0, this.fire);
            this.xframe = "shoot";
        }

        internal function frame30():*
        {
            stop();
        }

        internal function frame31():*
        {
            if (!this.self.getMetalStatus())
            {
                this.playsound = SSF2API.random();
                if ((this.playsound > 0) && (this.playsound <= 0.25))
                {
                    this.self.playSound("chibi_Spoon1");
                };
                if ((this.playsound > 0.25) && (this.playsound <= 0.5))
                {
                    this.self.playSound("chibi_Spoon2");
                };
                if ((this.playsound > 0.5) && (this.playsound <= 0.75))
                {
                    this.self.playSound("chibi_Spoon3");
                };
                if ((this.playsound > 0.75) && (this.playsound <= 1))
                {
                    this.self.playSound("chibi_Spoon4");
                };
            };
            this.xframe = "fire";
            this.self.updateAttackStats({"linkFrames":false});
            this.self.attachEffect("global_dust_light");
        }

        internal function frame39():*
        {
            if (this.controls.BUTTON1)
            {
                this.self.stancePlayFrame(this.redirectBlaster);
            }
            else
            {
                this.self.endAttack();
            };
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            };
        }


    }
}

