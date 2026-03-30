package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class KrystalKirby_249 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var top:MovieClip;
        public var self:KirbyExt;
        public var end:*;
        public var canContinue:*;
        public var proj:*;
        public var angle:*;
        public var fire:*;
        public var effect:*;
        public var proper:*;
        public var reversed:*;
        public var grounded:*;
        public var controls:Object;

        public function KrystalKirby_249()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9, 13, this.frame14, 14, this.frame15, 15, this.frame16, 44, this.frame45);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function toGround(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.grounded = true;
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        public function doIt():*
        {
            this.controls = this.self.getControls();
            if (this.self.isFacingRight() && this.controls.LEFT && !(this.controls.RIGHT))
            {
                this.self.faceLeft();
            }
            else if (!(this.self.isFacingRight()) && this.controls.RIGHT && !(this.controls.LEFT))
            {
                this.self.faceRight();
            };
            this.self.createTimer(1, -1, this.aim);
            this.proper = true;
        }

        public function aim(_arg_1:*=null):*
        {
            this.controls = this.self.getControls();
            if (this.controls.UP && !(this.controls.DOWN) && (this.angle < 30))
            {
                this.angle += 3;
            }
            else if (this.controls.DOWN && !(this.controls.UP) && (this.angle > -30))
            {
                this.angle -= 3;
            };
            if (this.angle < 0)
            {
                this.top.y = (48 + (-(this.angle) / 30));
            }
            else
            {
                this.top.y = 48;
            };
            this.top.rotation = -(this.angle);
            if (!(this.controls.BUTTON1) && this.fire)
            {
                if (!this.grounded)
                {
                    if (this.self.isFacingRight() && this.controls.LEFT && !(this.controls.RIGHT))
                    {
                        this.self.faceLeft();
                        this.reversed = true;
                    }
                    else if (!(this.self.isFacingRight()) && this.controls.RIGHT && !(this.controls.LEFT))
                    {
                        this.self.faceRight();
                        this.reversed = true;
                    };
                };
                this.self.setGlobalVariable("fired", false);
                this.self.stancePlayFrame("fire");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.end = false;
            this.canContinue = false;
            this.angle = 0;
            this.fire = false;
            this.proper = false;
            this.reversed = false;
            this.grounded = false;
            if (SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                if (this.self.isOnGround())
                {
                    this.grounded = true;
                }
                else
                {
                    this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
                };
            };
        }

        internal function frame4():*
        {
            this.self.playAttackSound(3);
        }

        internal function frame9():*
        {
            this.doIt();
        }

        internal function frame14():*
        {
            if (!(this.proper) && this.grounded)
            {
                this.angle = this.self.getGlobalVariable("angle");
                this.doIt();
            };
            this.fire = true;
        }

        internal function frame15():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame16():*
        {
            SSF2API.getCamera().shake(4);
            this.self.destroyTimer(this.aim);
            if (this.self.getGlobalVariable("fired") == false)
            {
                this.effect = this.self.attachEffect("krystal_rifleEffect", {
                    "x":this.self.flipX(46),
                    "y":-26.5
                });
                this.self.attachEffect("global_spark", {
                    "x":this.flipX(25),
                    "y":-24
                });
                if (this.grounded)
                {
                    this.self.attachEffect("global_dust_heavy", {
                        "x":this.flipX(20),
                        "scaleX":0.7,
                        "scaleY":0.3
                    });
                };
                this.proj = this.self.fireProjectile("krystal_snipe");
                this.proj.setGlobalVariable("reversed", this.reversed);
                if (this.self.isFacingRight())
                {
                    this.proj.angleControl(50, this.angle);
                    this.proj.setRotation(-(this.angle));
                    this.effect.rotation = -(this.angle);
                    this.proj.setX((this.proj.getX() - Math.abs(this.angle)));
                    this.effect.x -= Math.abs(this.angle);
                }
                else
                {
                    this.proj.angleControl(50, (180 - this.angle));
                    this.proj.setRotation(this.angle);
                    this.effect.rotation = this.angle;
                    this.proj.setX((this.proj.getX() + Math.abs(this.angle)));
                    this.effect.x += Math.abs(this.angle);
                };
                this.proj.setY((this.proj.getY() - (this.angle / 6)));
                this.effect.y -= (this.angle / 6);
                if (this.grounded)
                {
                    this.self.setXSpeed((this.self.getXSpeed() - (this.proj.getXSpeed() / 8)));
                }
                else
                {
                    this.self.setXSpeed((this.self.getXSpeed() - (this.proj.getXSpeed() / 6)));
                    this.self.setYSpeed((this.self.getYSpeed() - (this.proj.getYSpeed() / 2.5)));
                };
                this.self.playAttackSound(1);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("kirby_krystal", true);
                };
            };
        }

        internal function frame45():*
        {
            this.self.playAttackSound(2);
            this.self.endAttack();
        }


    }
}

