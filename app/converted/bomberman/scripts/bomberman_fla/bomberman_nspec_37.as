package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_nspec_37 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var pLockBox:MovieClip;
        public var self:BombermanExt;
        public var skipped:*;
        public var xframe:String;
        public var action:String;
        public var duration:*;
        public var controls:*;
        public var bomb:*;
        public var bombLimit:int;
        public var dir:*;
        public var projectile:Object;

        public function bomberman_nspec_37()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 31, this.frame32, 32, this.frame33, 38, this.frame39, 46, this.frame47, 47, this.frame48, 48, this.frame49, 52, this.frame53, 53, this.frame54, 56, this.frame57, 57, this.frame58, 59, this.frame60, 60, this.frame61, 65, this.frame66, 66, this.frame67, 71, this.frame72, 72, this.frame73, 73, this.frame74, 74, this.frame75, 79, this.frame80, 80, this.frame81, 83, this.frame84);
        }

        public function drop():void
        {
            this.controls = this.self.getControls();
            if (!(this.controls.BUTTON1) && this.controls.DOWN)
            {
                SSF2API.print("dropping");
                this.self.destroyTimer(this.drop);
                gotoAndStop("drop");
            }
            else if (this.controls.JUMP || this.controls.JUMP2 || (this.controls.TAP_JUMP && this.controls.UP))
            {
                SSF2API.print("jumping");
                this.self.destroyTimer(this.drop);
                gotoAndStop("jumpStart");
            };
        }

        public function throwUp():void
        {
            this.duration++;
            this.controls = this.self.getControls();
            if (!(this.controls.BUTTON1) && this.controls.UP)
            {
                SSF2API.print("Up!");
                this.skipped = false;
                this.self.destroyTimer(this.throwUp);
                gotoAndStop("up");
            };
        }

        public function garbageCollect():void
        {
            var _local_1:int;
            if (this.self.bombArray != null)
            {
            for (_local_1 = 0; _local_1 < this.self.bombArray.length; _local_1++)
            {
                    this.bomb = this.self.bombArray[_local_1];
                    if (this.bomb.isDisposed() || this.bomb.inState(PState.DEAD))
                    {
                        this.self.bombArray.splice(_local_1--, 1);
                    };
                };
            };
        }

        public function flipX(_arg_1:Number):*
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            this.skipped = false;
            this.duration = 0;
            this.xframe = "charging";
            this.action = "standing";
            if (this.self && SSF2API.isReady())
            {
                this.dir = this.self.isFacingRight();
                this.bombLimit = this.self.MAX_BOMBS;
                if (this.self.getGlobalVariable("bombCharge") == null)
                {
                    this.self.fireProjectile("heldbomb");
                    this.projectile = this.self.getCurrentProjectile();
                    this.self.setGlobalVariable("bombCharge", this.projectile);
                }
                else
                {
                    gotoAndStop("standing");
                };
            };
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(10),
                "y":-20
            });
            this.self.createTimer(1, -1, this.drop);
            this.self.createTimer(1, -1, this.throwUp);
        }

        internal function frame11():*
        {
            this.self.destroyTimer(this.throwUp);
            this.self.createTimer(1, -1, this.throwUp);
            this.self.destroyTimer(this.drop);
            this.self.createTimer(1, -1, this.drop);
            this.xframe = "charging";
            this.action = "standing";
            this.self.updateAttackStats({
                "allowControl":false,
                "allowRun":true
            });
        }

        internal function frame32():*
        {
            gotoAndStop("standing");
        }

        internal function frame33():*
        {
            this.self.destroyTimer(this.throwUp);
            this.self.createTimer(1, -1, this.throwUp);
            this.self.destroyTimer(this.drop);
            this.self.createTimer(1, -1, this.drop);
            this.xframe = "charging";
            this.action = "moving";
        }

        internal function frame39():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
        }

        internal function frame47():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            };
        }

        internal function frame48():*
        {
            gotoAndStop("moving");
        }

        internal function frame49():*
        {
            this.xframe = "charging";
            this.action = "rising";
            this.self.setYSpeed(0);
            this.self.updateAttackStats({
                "allowJump":false,
                "allowControl":false,
                "allowTurn":false,
                "allowRun":false,
                "linkFrames":false
            });
            this.controls = this.self.getControls();
            this.self.createTimer(-1, 1, this.throwUp);
            this.self.destroyTimer(this.drop);
        }

        internal function frame53():*
        {
            this.self.updateAttackStats({"linkFrames":true});
            this.self.destroyTimer(this.throwUp);
            this.controls = this.self.getControls();
            this.self.unnattachFromGround();
            if (this.controls.BUTTON1 && !(this.controls.JUMP) && !(this.controls.JUMP2))
            {
                if (this.controls.TAP_JUMP)
                {
                    if (!this.controls.UP)
                    {
                        this.skipped = true;
                        SSF2API.print("shorthop");
                    };
                }
                else
                {
                    this.skipped = true;
                    SSF2API.print("shorthop");
                };
            };
            if (this.skipped)
            {
                this.self.setYSpeed(-10);
            };
            if (!this.skipped)
            {
                this.self.setYSpeed(-18);
            };
        }

        internal function frame54():*
        {
            this.xframe = "attack";
            this.self.updateAttackStats({
                "allowJump":false,
                "allowControl":false,
                "allowTurn":false,
                "allowRun":false,
                "linkFrames":false
            });
            this.self.setGlobalVariable("charge", this.self.getAttackStat("chargetime"));
            this.throwUp();
            this.drop();
            this.self.destroyTimer(this.drop);
            this.self.destroyTimer(this.throwUp);
        }

        internal function frame57():*
        {
            this.throwUp();
        }

        internal function frame58():*
        {
            this.throwUp();
        }

        internal function frame60():*
        {
            this.self.playAttackSound(1);
            this.controls = this.self.getControls();
            this.dir = this.self.isFacingRight();
            this.garbageCollect();
            if ((this.self.bombArray.length - 1) >= (this.bombLimit - 1))
            {
                this.self.bombArray.shift().destroy();
            };
            this.projectile = this.self.getGlobalVariable("bombCharge");
            if (this.projectile && !(this.projectile.isDisposed()) && (this.projectile.getStanceMC().currentLabel == "1"))
            {
                this.bomb = this.self.fireProjectile("bomb1dropped", this.projectile.getX(), this.projectile.getY(), true);
            }
            else if (this.projectile && !(this.projectile.isDisposed()) && (this.projectile.getStanceMC().currentLabel == "2"))
            {
                this.bomb = this.self.fireProjectile("bomb2dropped", this.projectile.getX(), this.projectile.getY(), true);
            }
            else if (this.projectile && !(this.projectile.isDisposed()))
            {
                this.bomb = this.self.fireProjectile("bomb3dropped", this.projectile.getX(), this.projectile.getY(), true);
            };
            if (this.projectile && !(this.projectile.isDisposed()))
            {
                this.projectile.destroy();
            };
            this.self.setGlobalVariable("bombCharge", null);
            this.self.bombArray.push(this.bomb);
            if (this.dir)
            {
                this.bomb.setXSpeed(8);
            }
            else
            {
                this.bomb.setXSpeed(-8);
            };
            this.bomb.setYSpeed(-9);
        }

        internal function frame61():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(-5),
                "y":-40
            });
        }

        internal function frame66():*
        {
            this.self.endAttack();
        }

        internal function frame67():*
        {
            this.xframe = "attack";
            this.self.updateAttackStats({
                "allowJump":false,
                "allowControl":false,
                "allowTurn":false,
                "allowRun":false,
                "linkFrames":false
            });
            this.self.setGlobalVariable("charge", this.self.getAttackStat("chargetime"));
            this.self.destroyTimer(this.drop);
            this.self.destroyTimer(this.throwUp);
        }

        internal function frame72():*
        {
            this.self.playAttackSound(1);
            this.controls = this.self.getControls();
            this.dir = this.self.isFacingRight();
            this.garbageCollect();
            if ((this.self.bombArray.length - 1) >= (this.bombLimit - 1))
            {
                this.self.bombArray.shift().destroy();
            };
            this.projectile = this.self.getGlobalVariable("bombCharge");
            if (this.projectile && !(this.projectile.isDisposed()) && (this.projectile.getStanceMC().currentLabel == "1"))
            {
                this.bomb = this.self.fireProjectile("bomb1dropped", this.projectile.getX(), this.projectile.getY(), true);
            }
            else if (this.projectile && !(this.projectile.isDisposed()) && (this.projectile.getStanceMC().currentLabel == "2"))
            {
                this.bomb = this.self.fireProjectile("bomb2dropped", this.projectile.getX(), this.projectile.getY(), true);
            }
            else if (this.projectile && !(this.projectile.isDisposed()))
            {
                this.bomb = this.self.fireProjectile("bomb3dropped", this.projectile.getX(), this.projectile.getY(), true);
            };
            if (this.projectile && !(this.projectile.isDisposed()))
            {
                this.projectile.destroy();
            };
            this.bomb.setYSpeed((this.self.getYSpeed() + 2));
            this.self.setGlobalVariable("bombCharge", null);
            this.self.bombArray.push(this.bomb);
        }

        internal function frame73():*
        {
            this.self.attachEffect("global_spark", {"x":this.flipX(5)});
        }

        internal function frame74():*
        {
            this.self.endAttack();
        }

        internal function frame75():*
        {
            this.xframe = "attack";
            this.self.updateAttackStats({
                "allowJump":false,
                "allowControl":false,
                "allowTurn":false,
                "allowRun":false,
                "linkFrames":false
            });
            this.self.setGlobalVariable("charge", this.self.getAttackStat("chargetime"));
            this.self.destroyTimer(this.drop);
        }

        internal function frame80():*
        {
            this.self.playAttackSound(1);
            this.controls = this.self.getControls();
            this.dir = this.self.isFacingRight();
            this.garbageCollect();
            if ((this.self.bombArray.length - 1) >= (this.bombLimit - 1))
            {
                this.self.bombArray.shift().destroy();
            };
            this.projectile = this.self.getGlobalVariable("bombCharge");
            if (this.projectile && !(this.projectile.isDisposed()) && (this.projectile.getStanceMC().currentLabel == "1"))
            {
                this.bomb = this.self.fireProjectile("bomb1dropped", this.projectile.getX(), this.projectile.getY(), true);
            }
            else if (this.projectile && !(this.projectile.isDisposed()) && (this.projectile.getStanceMC().currentLabel == "2"))
            {
                this.bomb = this.self.fireProjectile("bomb2dropped", this.projectile.getX(), this.projectile.getY(), true);
            }
            else if (this.projectile && !(this.projectile.isDisposed()))
            {
                this.bomb = this.self.fireProjectile("bomb3dropped", this.projectile.getX(), this.projectile.getY(), true);
            };
            if (this.projectile && !(this.projectile.isDisposed()))
            {
                this.projectile.destroy();
            };
            this.self.setGlobalVariable("bombCharge", null);
            this.self.bombArray.push(this.bomb);
            this.bomb.setXSpeed(0);
            this.bomb.setYSpeed(-20);
        }

        internal function frame81():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(-7),
                "y":-48
            });
        }

        internal function frame84():*
        {
            this.self.endAttack();
        }


    }
}

