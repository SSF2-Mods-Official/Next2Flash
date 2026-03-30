package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class NeutralSpecial_Air__44 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var redirectBlaster:*;
        public var projectile:*;
        public var hasntFired:*;
        public var playsound:*;
        public var xframe:*;
        public var controls:Object;
        public var localBlaster:*;

        public function NeutralSpecial_Air__44()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 28, this.frame29, 29, this.frame30, 34, this.frame35);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function refreshTimers():void
        {
            this.self.destroyTimer(this.testButton);
            this.self.destroyTimer(this.fire);
            this.self.createTimer(1, 0, this.testButton);
            this.self.createTimer(10, 0, this.fire);
        }

        public function initTimers():*
        {
            this.self.destroyTimer(this.testButton);
            this.self.destroyTimer(this.fire);
            this.self.createTimer(1, 0, this.testButton);
            this.self.createTimer(3, 0, this.fire);
        }

        public function testButton():void
        {
            this.controls = this.self.getControls();
            this.localBlaster = this.self.getGlobalVariable("blasterAngle");
            if (this.controls.BUTTON1 || this.hasntFired)
            {
                if (this.controls.DOWN && (this.localBlaster > 270))
                {
                    this.localBlaster -= 10;
                }
                else if (this.controls.UP && (this.localBlaster < 360))
                {
                    this.localBlaster += 10;
                };
                if (this.currentLabel != "fire")
                {
                    this.self.setGlobalVariable("blasterAngle", this.localBlaster);
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
            if (this.localBlaster == 360)
            {
                this.self.fireProjectile("chibi_blaster", -8, 4);
            }
            else if (this.localBlaster == 350)
            {
                this.self.fireProjectile("chibi_blaster", -6, 6);
            }
            else if (this.localBlaster == 340)
            {
                this.self.fireProjectile("chibi_blaster", -4, 8);
            }
            else if (this.localBlaster == 330)
            {
                this.self.fireProjectile("chibi_blaster", -2, 10);
            }
            else if (this.localBlaster == 320)
            {
                this.self.fireProjectile("chibi_blaster", 0, 12);
            }
            else if (this.localBlaster == 310)
            {
                this.self.fireProjectile("chibi_blaster", 2, 14);
            }
            else if (this.localBlaster == 300)
            {
                this.self.fireProjectile("chibi_blaster", 0, 16);
            }
            else if (this.localBlaster == 290)
            {
                this.self.fireProjectile("chibi_blaster", -2, 18);
            }
            else if (this.localBlaster == 280)
            {
                this.self.fireProjectile("chibi_blaster", -8, 20);
            }
            else if (this.localBlaster == 270)
            {
                this.self.fireProjectile("chibi_blaster", -12, 22);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.hasntFired = true;
            this.xframe = "startup";
            if (this.self && SSF2API.isReady())
            {
                this.controls = this.self.getControls();
                this.self.setGlobalVariable("blasterAngle", 360);
                this.self.destroyTimer(this.testButton);
                this.self.destroyTimer(this.fire);
                this.localBlaster = this.self.getGlobalVariable("blasterAngle");
                if (this.localBlaster == null)
                {
                    this.localBlaster = 360;
                };
                this.self.attachEffect("global_spark", {
                    "x":this.flipX(23),
                    "y":-30
                });
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            };
        }

        internal function frame6():*
        {
            this.initTimers();
            this.xframe = "shoot";
        }

        internal function frame29():*
        {
            stop();
        }

        internal function frame30():*
        {
            this.hasntFired = false;
            this.xframe = "fire";
            this.refreshTimers();
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
            this.self.updateAttackStats({"linkFrames":false});
            this.self.attachEffect("global_dust_light");
        }

        internal function frame35():*
        {
            if (this.controls.BUTTON1)
            {
                this.self.stancePlayFrame(this.redirectBlaster);
            }
            else
            {
                this.self.endAttack();
            };
        }


    }
}

