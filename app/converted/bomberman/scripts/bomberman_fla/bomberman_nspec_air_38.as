package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_nspec_air_38 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var pLockBox:MovieClip;
        public var xframe:String;
        public var action:String;
        public var controls:*;
        public var bomb:*;
        public var bombLimit:int;
        public var self:BombermanExt;
        public var dir:*;
        public var projectile:Object;

        public function bomberman_nspec_air_38()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 19, this.frame20, 28, this.frame29, 29, this.frame30, 34, this.frame35, 35, this.frame36, 36, this.frame37, 39, this.frame40, 41, this.frame42, 47, this.frame48, 48, this.frame49, 54, this.frame55, 56, this.frame57, 58, this.frame59, 59, this.frame60, 65, this.frame66, 67, this.frame68, 69, this.frame70);
        }

        public function drop():void
        {
            this.controls = this.self.getControls();
            if (!(this.controls.BUTTON1) && this.controls.DOWN)
            {
                SSF2API.print("dropping");
                gotoAndStop("drop");
            }
            else if (!(this.controls.BUTTON1) && this.controls.UP)
            {
                SSF2API.print("throwing up");
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
            this.xframe = "charging";
            this.action = "rising";
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (this.self && SSF2API.isReady())
            {
                if (this.self.getGlobalVariable("bombCharge") == null)
                {
                    this.self.fireProjectile("heldbomb");
                    this.dir = this.self.isFacingRight();
                    this.projectile = this.self.getCurrentProjectile();
                    this.self.setGlobalVariable("bombCharge", this.projectile);
                    this.self.attachEffect("global_sparkle", {
                        "x":this.flipX(10),
                        "y":-20
                    });
                };
                this.bombLimit = this.self.MAX_BOMBS;
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, -1, this.drop);
            gotoAndStop("rising");
        }

        internal function frame20():*
        {
            this.self.updateAttackStats({
                "allowControl":true,
                "allowTurn":true
            });
            this.xframe = "charging";
            this.action = "rising";
        }

        internal function frame29():*
        {
            gotoAndStop("rising");
        }

        internal function frame30():*
        {
            this.xframe = "charging";
            this.action = "falling";
            this.self.updateAttackStats({
                "allowControl":true,
                "allowTurn":true
            });
        }

        internal function frame35():*
        {
            gotoAndStop("fallingloop");
        }

        internal function frame36():*
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
        }

        internal function frame37():*
        {
            this.self.destroyTimer(this.drop);
        }

        internal function frame40():*
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
                this.bomb = this.self.fireProjectile("bomb1dropped");
            }
            else if (this.projectile && !(this.projectile.isDisposed()) && (this.projectile.getStanceMC().currentLabel == "2"))
            {
                this.bomb = this.self.fireProjectile("bomb2dropped");
            }
            else
            {
                this.bomb = this.self.fireProjectile("bomb3dropped");
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

        internal function frame42():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(-5),
                "y":-40
            });
        }

        internal function frame48():*
        {
            this.self.endAttack();
        }

        internal function frame49():*
        {
            this.self.destroyTimer(this.drop);
            this.xframe = "attack";
            this.self.updateAttackStats({
                "allowJump":false,
                "allowFastFall":false,
                "allowControl":false,
                "allowTurn":false,
                "allowRun":false,
                "linkFrames":false
            });
            this.self.setGlobalVariable("charge", this.self.getAttackStat("chargetime"));
            this.self.destroyTimer(this.drop);
        }

        internal function frame55():*
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
            this.self.bombArray.push(this.self.getCurrentProjectile());
        }

        internal function frame57():*
        {
            this.self.attachEffect("global_spark", {"x":this.flipX(5)});
        }

        internal function frame59():*
        {
            this.self.endAttack();
        }

        internal function frame60():*
        {
            this.self.destroyTimer(this.drop);
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

        internal function frame66():*
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

        internal function frame68():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(-7),
                "y":-48
            });
        }

        internal function frame70():*
        {
            this.self.endAttack();
        }


    }
}

