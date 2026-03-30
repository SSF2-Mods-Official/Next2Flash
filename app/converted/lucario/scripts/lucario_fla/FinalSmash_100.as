package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmash_100 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var self:LucarioExt;
        public var speed:Number;
        public var attackDuration:*;
        public var fallen:Boolean;
        public var proj:*;
        public var controls:*;
        public var startingFace:Boolean;
        public var angle:*;
        public var endAngle:*;
        public var rotAmount:*;
        public var beamsfx:*;

        public function FinalSmash_100()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 11, this.frame12, 17, this.frame18, 18, this.frame19, 21, this.frame22, 22, this.frame23, 23, this.frame24, 24, this.frame25, 26, this.frame27, 45, this.frame46, 47, this.frame48, 53, this.frame54, 57, this.frame58, 61, this.frame62, 68, this.frame69, 69, this.frame70, 79, this.frame80, 86, this.frame87, 88, this.frame89, 98, this.frame99, 99, this.frame100);
        }

        public function flyUp(_arg_1:*=null):*
        {
            if (this.speed < 40)
            {
                this.speed += 4;
            };
            if ((this.self.getY() - this.speed) > SSF2API.getStage().getDeathBounds().y)
            {
                this.self.setY((this.self.getY() - this.speed));
            }
            else
            {
                this.self.setY((SSF2API.getStage().getDeathBounds().y + 50));
                this.self.destroyTimer(this.flyUp);
                this.self.setX((SSF2API.getStage().getCameraBounds().x + (SSF2API.getStage().getCameraBounds().width / 2)));
                this.self.stancePlayFrame("fall");
            };
        }

        public function floatDown(_arg_1:*=null):*
        {
            if (this.speed > 0.1)
            {
                if (this.self.getY() > SSF2API.getStage().getCameraBounds().y)
                {
                    this.speed *= 0.9;
                    if (!this.fallen)
                    {
                        this.self.stancePlayFrame("reallyFall");
                        this.fallen = true;
                    };
                };
                this.self.setY((this.self.getY() + this.speed));
            }
            else
            {
                this.speed = 0;
                this.self.destroyTimer(this.floatDown);
            };
        }

        public function fire():*
        {
            this.proj = this.self.fireProjectile("lucario_fsbeam", 5, -6);
            this.self.swapDepths(this.proj);
            this.self.createTimer(1, -1, this.updateFireLoop);
            this.startingFace = this.self.isFacingRight();
            this.beamsfx = this.self.playSound("lucario_fs_beamsfx");
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("lucario_fs_attack", true);
            };
        }

        public function endFire():*
        {
            this.proj.stancePlayFrame("end");
            this.self.stancePlayFrame("end");
            this.self.destroyTimer(this.updateFireLoop);
        }

        public function updateFireLoop(_arg_1:*=null):*
        {
            if (this.attackDuration > 0)
            {
                SSF2API.getCamera().shake(3);
                this.controls = this.self.getControls();
                if (this.controls.RIGHT && !(this.controls.LEFT) && (this.angle > -60))
                {
                    this.angle -= 0.8;
                }
                else if (this.controls.LEFT && !(this.controls.RIGHT) && (this.angle < 60))
                {
                    this.angle += 0.8;
                };
                if ((this.angle > 0) || (!(this.startingFace) && (this.angle == 0)))
                {
                    this.self.faceLeft();
                }
                else if ((this.angle < 0) || (this.startingFace && (this.angle == 0)))
                {
                    this.self.faceRight();
                };
                this.self.setRotation(this.angle);
                this.proj.setRotation(this.angle);
                this.attackDuration--;
            }
            else
            {
                this.endFire();
            };
        }

        public function rotateBack(_arg_1:*=null):*
        {
            this.self.setRotation((this.endAngle * this.rotAmount));
            if (this.rotAmount > 0)
            {
                this.rotAmount--;
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.speed = 0;
            this.attackDuration = 150;
            this.fallen = false;
            this.angle = 0;
            this.endAngle = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
                this.self.camFocus(25);
            };
        }

        internal function frame7():*
        {
            this.self.playSound("lucario_step1");
            this.self.attachEffect("effect_land");
        }

        internal function frame12():*
        {
            this.self.playSound("lucario_dspec");
        }

        internal function frame18():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("lucario_fs_maxaura", true);
            };
        }

        internal function frame19():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame22():*
        {
            this.self.createTimer(1, -1, this.flyUp);
            this.self.playSound("lucario_fs_jumpsfx");
        }

        internal function frame23():*
        {
            this.self.attachEffect("lucario_uspec_trail", {
                "x":this.self.flipX(-12),
                "y":-31,
                "rotation":270,
                "behind":true,
                "scaleX":(Math.abs(this.speed) / 15)
            });
            this.self.attachEffect("lucario_uspec_trail", {
                "x":this.self.flipX(13),
                "y":-31,
                "rotation":270,
                "behind":true,
                "scaleX":(Math.abs(this.speed) / 15)
            });
        }

        internal function frame24():*
        {
            this.self.stancePlayFrame("flyLoop");
        }

        internal function frame25():*
        {
            this.speed = 10;
            this.self.createTimer(1, -1, this.floatDown);
        }

        internal function frame27():*
        {
            this.self.stancePlayFrame("fallLoop");
        }

        internal function frame46():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame48():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame54():*
        {
            this.self.updateAuraPaws();
            this.self.playSound("lucario_fs_startsfx");
        }

        internal function frame58():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame62():*
        {
            this.fire();
        }

        internal function frame69():*
        {
            this.self.stancePlayFrame("fireLoop");
        }

        internal function frame70():*
        {
            this.self.stopSound(this.beamsfx);
            this.self.playSound("lucario_fs_endsfx");
        }

        internal function frame80():*
        {
            this.endAngle = (this.self.getRotation() / 10);
            this.rotAmount = 10;
            this.self.createTimer(1, 11, this.rotateBack);
        }

        internal function frame87():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame89():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame99():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame100():*
        {
            this.self.endAttack();
        }


    }
}

