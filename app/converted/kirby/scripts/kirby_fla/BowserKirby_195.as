package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class BowserKirby_195 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;
        public var controls:*;
        public var sfxStop:int;
        public var nspec:int;
        public var maxAngle:*;
        public var minAngle:*;
        public var minAngleAir:*;
        public var angleSteps:*;
        public var defaultSize:*;
        public var minSize:*;
        public var sizeSteps:*;
        public var flameSpeed:*;
        public var currentStep:*;
        public var currentStepAngle:*;
        public var time:int;
        public var proj:*;
        public var flameTime:int;
        public var loops:*;
        public var maxTime:*;
        public var minTime:*;
        public var timeSteps:*;

        public function BowserKirby_195()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 11, this.frame12, 12, this.frame13, 23, this.frame24, 33, this.frame34);
        }

        public function angle(_arg_1:*=null):void
        {
            this.controls = this.self.getControls();
            if (this.controls.UP)
            {
                this.currentStep++;
            }
            else if (this.controls.DOWN)
            {
                this.currentStep--;
            };
            if (this.currentStep < 0)
            {
                this.currentStep = 0;
            }
            else if (this.currentStep > this.angleSteps)
            {
                this.currentStep = this.angleSteps;
            };
            this.currentStepAngle = (this.minAngle + (((Math.abs(this.maxAngle) + Math.abs(this.minAngle)) / this.angleSteps) * this.currentStep));
            SSF2API.print(((("" + this.currentStepAngle) + ",") + this.currentStep));
        }

        public function checkFinish():void
        {
            if (!this.controls.BUTTON1)
            {
                this.self.destroyTimer(this.checkFinish);
                this.gotoAndStop("continue");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.xframe = null;
            this.controls = null;
            this.sfxStop = 0;
            this.nspec = 1;
            this.maxAngle = 35;
            this.minAngle = -65;
            this.minAngleAir = -40;
            this.angleSteps = 12;
            this.defaultSize = 2.45;
            this.minSize = 1.35;
            this.sizeSteps = 90;
            this.flameSpeed = 10;
            this.currentStep = (this.angleSteps / 3);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setupHatEffect(1, 0, -16);
                if (this.self.isOnGround())
                {
                    this.currentStep = (this.angleSteps * 0.6);
                }
                else
                {
                    this.self.updateAttackStats({"cancelWhenAirborne":true});
                };
            };
            this.currentStepAngle = (this.minAngle + (((Math.abs(this.maxAngle) + Math.abs(this.minAngle)) / this.angleSteps) * this.currentStep));
            if (this.self && SSF2API.isReady())
            {
                this.self.createTimer(5, 0, this.angle);
            };
        }

        internal function frame11():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("kirby_footstep");
            };
        }

        internal function frame12():*
        {
            this.flameTime = 0;
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
            this.loops = 4;
            this.self.updateAttackStats({"air_ease":10});
        }

        internal function frame13():*
        {
            this.maxTime = 10;
            this.minTime = 8;
            this.timeSteps = this.sizeSteps;
            SSF2API.getCamera().shake(4);
            this.self.fireProjectile("fireBreath", 15, -18);
            this.proj = this.self.getCurrentProjectile();
            this.time = (this.self.getExecTime() - 13);
            if (this.time < 0)
            {
                this.time = 0;
            };
            if ((this.defaultSize * (this.minSize - (this.time / this.sizeSteps))) >= this.minSize)
            {
                this.proj.setScale((this.defaultSize * (this.minSize - (this.time / this.sizeSteps))), (this.defaultSize * (this.minSize - (this.time / this.sizeSteps))));
                this.flameTime = (this.minTime + (this.maxTime - (this.time / (this.timeSteps / this.maxTime))));
            }
            else
            {
                this.proj.setScale(this.minSize, this.minSize);
                this.flameTime = this.minTime;
            };
            this.proj.updateProjectileStats({"time_max":this.flameTime});
            if (this.self.isFacingRight())
            {
                this.proj.angleControl(this.flameSpeed, this.currentStepAngle);
            }
            else
            {
                this.proj.angleControl(this.flameSpeed, (180 - this.currentStepAngle));
                this.proj.flip();
                this.proj.updateAttackBoxStats(1, {"direction":130});
            };
            this.self.attachEffect("global_dust_heavy");
            this.self.setXSpeed((this.self.getXSpeed() + this.self.flipX(-8)));
            if (!this.self.isOnGround())
            {
                this.self.setYSpeed((this.self.getYSpeed() - 5));
            };
        }

        internal function frame24():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }


    }
}

