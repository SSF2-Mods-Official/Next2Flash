package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Chibi_RoboKirby_227 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var redirectBlaster:*;
        public var projectile:*;
        public var hasntFired:*;
        public var playsound:*;
        public var xframe:*;
        public var controls:Object;
        public var localBlaster:*;
        public var tails_ground:Boolean;

        public function Chibi_RoboKirby_227()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 29, this.frame30, 30, this.frame31, 38, this.frame39, 40, this.frame41, 45, this.frame46, 68, this.frame69, 69, this.frame70, 74, this.frame75);
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
                    gotoAndStop(this.redirectBlaster);
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
            this.gotoAndStop("fire");
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

        public function refreshTimers():void
        {
            this.self.destroyTimer(this.airTestButton);
            this.self.destroyTimer(this.airFire);
            this.self.createTimer(1, 0, this.airTestButton);
            this.self.createTimer(10, 0, this.airFire);
        }

        public function initTimers():*
        {
            this.self.destroyTimer(this.airTestButton);
            this.self.destroyTimer(this.airFire);
            this.self.createTimer(1, 0, this.airTestButton);
            this.self.createTimer(3, 0, this.airFire);
        }

        public function airTestButton():void
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
                if (this.currentLabel != "airFire")
                {
                    this.self.setGlobalVariable("blasterAngle", this.localBlaster);
                    this.redirectBlaster = ("degree" + this.localBlaster);
                    gotoAndStop(this.redirectBlaster);
                };
            }
            else if (this.currentLabel != "airFire")
            {
                this.self.destroyTimer(this.airTestButton);
                this.self.destroyTimer(this.airFire);
                this.self.endAttack();
            };
        }

        public function airFire():void
        {
            this.gotoAndStop("airFire");
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
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
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
                this.tails_ground = this.self.isOnGround();
                if (!this.tails_ground)
                {
                    this.self.setGlobalVariable("blasterAngle", 360);
                    gotoAndStop("chibi_air");
                };
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
            this.xframe = "fire";
        }

        internal function frame39():*
        {
            if (this.controls.BUTTON1)
            {
                gotoAndStop(this.redirectBlaster);
            }
            else
            {
                this.self.endAttack();
            };
        }

        internal function frame41():*
        {
            this.self.destroyTimer(this.testButton);
            this.self.destroyTimer(this.fire);
            this.localBlaster = this.self.getGlobalVariable("blasterAngle");
            if ((this.localBlaster == null) || (this.localBlaster == 0))
            {
                this.localBlaster = 360;
            };
        }

        internal function frame46():*
        {
            this.initTimers();
            this.xframe = "airShoot";
        }

        internal function frame69():*
        {
            stop();
        }

        internal function frame70():*
        {
            this.hasntFired = false;
            this.xframe = "airFire";
            this.refreshTimers();
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
        }

        internal function frame75():*
        {
            if (this.controls.BUTTON1)
            {
                gotoAndStop(this.redirectBlaster);
            }
            else
            {
                this.self.endAttack();
            };
        }


    }
}

