package lucario_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class UpSpecial_41 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var controls:*;
        public var angle:*;
        public var speed:*;
        public var angleStep:*;
        public var flyTimer:*;
        public var startControls:Array;
        public var flyState:Number;
        public var flyDirect:String;
        public var stepper:Number;
        public var flyFrame:Number;
        public var heavyLand:Boolean;
        public var heavyLand2:Boolean;
        public var angles:Array;
        public var prevHand1:Point;
        public var prevHand2:Point;
        public var currHand1:Point;
        public var currHand2:Point;
        public var effAng1:*;
        public var effDist1:*;
        public var effAng2:*;
        public var effDist2:*;
        public var speedDist:*;
        public var pos1X:Array;
        public var pos1Y:Array;
        public var pos2X:Array;
        public var pos2Y:Array;
        public var pos1L:Array;
        public var pos2L:Array;
        public var attackAngle:*;

        public function UpSpecial_41()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 8, this.frame9, 35, this.frame36, 37, this.frame38, 39, this.frame40, 45, this.frame46, 50, this.frame51, 51, this.frame52, 52, this.frame53, 60, this.frame61, 61, this.frame62, 62, this.frame63, 64, this.frame65, 74, this.frame75, 78, this.frame79, 80, this.frame81, 81, this.frame82, 82, this.frame83, 104, this.frame105, 106, this.frame107, 107, this.frame108, 108, this.frame109, 115, this.frame116);
        }

        public function stepAngle(_arg_1:Number):*
        {
            this.angle += _arg_1;
            if (this.angle < 0)
            {
                this.angle = (360 - Math.abs(this.angle));
            }
            else if (this.angle > 360)
            {
                this.angle -= 360;
            };
            if (this.groundBelow() && (this.angle > 90) && (this.angle <= 105))
            {
                this.angle = 90;
            }
            else if (this.groundBelow() && (this.angle < 270) && (this.angle >= 255))
            {
                this.angle = 270;
            };
        }

        public function groundBelow():Boolean
        {
            if (SSF2API.hitTestGroundBetweenPoints(new Point(this.self.getX(), this.self.getY()), new Point(this.self.getX(), (this.self.getY() + 10))))
            {
                return true;
            }
            else
            if (this.self.isOnGround())
            {
                return true;
            }
            else
            {
            return false;
            };
        }

        public function land(_arg_1:*=null):*
        {
            this.resetStats();
            this.self.destroyTimer(this.fly);
            if ((this.currentFrame >= 22) && (this.currentFrame < 28))
            {
                this.self.stancePlayFrame("endSkid");
            }
            else if ((this.currentFrame >= 28) && (this.currentFrame < 36))
            {
                this.self.stancePlayFrame("endCrash");
            }
            else if ((this.currentFrame >= 36) && this.heavyLand2)
            {
                this.self.stancePlayFrame("specialLand");
            }
            else if ((this.currentFrame >= 36) && !(this.heavyLand2) && (this.angle >= 135) && (this.angle < 240))
            {
                this.self.stancePlayFrame("endCrash");
            }
            else if (((this.currentFrame >= 36) && !(this.heavyLand) && (this.angle >= 90) && (this.angle < 135)) || ((this.currentFrame >= 36) && !(this.heavyLand) && (this.angle >= 240) && (this.angle < 285)))
            {
                this.self.stancePlayFrame("endSkid");
            }
            else
            {
                this.self.stancePlayFrame("specialLand");
            };
        }

        public function updateAngle():*
        {
            this.self.updateAuraPaws();
            if ((this.angle > 0) && (this.angle < 180))
            {
                this.self.faceLeft();
                this.self.stancePlayFrame((10 + ((this.angle / 15) * 2)));
            }
            else if (this.angle > 180)
            {
                this.self.faceRight();
                this.self.stancePlayFrame((34 - ((Math.abs((-(this.angle) + 180)) / 15) * 2)));
            }
            else if (this.angle == 0)
            {
                if (this.currentFrame > 11)
                {
                    this.self.flip();
                };
                this.self.stancePlayFrame(10);
            }
            else if (this.angle == 180)
            {
                if (this.currentFrame < 34)
                {
                    this.self.flip();
                };
                this.self.stancePlayFrame(34);
            };
        }

        public function resetStartControls():*
        {
            this.controls = this.self.getControls();
            this.startControls[0] = this.controls.UP;
            this.startControls[1] = this.controls.DOWN;
            this.startControls[2] = this.controls.LEFT;
            this.startControls[3] = this.controls.RIGHT;
        }

        public function setFlyDirection():*
        {
            if (this.startControls[0] && !(this.startControls[1]))
            {
                if (this.startControls[2] && !(this.startControls[3]))
                {
                    this.flyDirect = "ul";
                }
                else if (this.startControls[3] && !(this.startControls[2]))
                {
                    this.flyDirect = "ur";
                }
                else
                {
                    this.flyDirect = "u";
                };
            }
            else if (this.startControls[1] && !(this.startControls[0]))
            {
                if (this.startControls[2] && !(this.startControls[3]))
                {
                    this.flyDirect = "dl";
                }
                else if (this.startControls[3] && !(this.startControls[2]))
                {
                    this.flyDirect = "dr";
                }
                else
                {
                    this.flyDirect = "d";
                };
            }
            else if (this.startControls[2] && !(this.startControls[3]))
            {
                this.flyDirect = "l";
            }
            else if (this.startControls[3] && !(this.startControls[2]))
            {
                this.flyDirect = "r";
            }
            else
            {
                this.flyDirect = "n";
            };
            if (this.flyDirect == "u")
            {
                if (this.angle > 180)
                {
                    this.stepper = 1;
                }
                else if (this.angle == 180)
                {
                    if (this.self.isFacingRight())
                    {
                        this.stepper = 1;
                    }
                    else
                    {
                        this.stepper = -1;
                    };
                }
                else if ((this.angle > 0) && (this.angle < 180))
                {
                    this.stepper = -1;
                };
            }
            else if (this.flyDirect == "ul")
            {
                if ((this.angle < 45) || (this.angle >= 225))
                {
                    this.stepper = 1;
                }
                else if ((this.angle > 45) && (this.angle < 225))
                {
                    this.stepper = -1;
                };
            }
            else if (this.flyDirect == "l")
            {
                if ((this.angle < 90) || (this.angle >= 270))
                {
                    this.stepper = 1;
                }
                else if ((this.angle > 90) && (this.angle < 270))
                {
                    this.stepper = -1;
                };
            }
            else if (this.flyDirect == "dl")
            {
                if ((this.angle < 135) || (this.angle >= 315))
                {
                    this.stepper = 1;
                }
                else if ((this.angle > 135) && (this.angle < 315))
                {
                    this.stepper = -1;
                };
            }
            else if (this.flyDirect == "d")
            {
                if ((this.angle < 180) && (this.angle > 0))
                {
                    this.stepper = 1;
                }
                else if (this.angle == 0)
                {
                    if (this.self.isFacingRight())
                    {
                        this.stepper = -1;
                    }
                    else
                    {
                        this.stepper = 1;
                    };
                }
                else if (this.angle > 180)
                {
                    this.stepper = -1;
                };
            }
            else if (this.flyDirect == "dr")
            {
                if ((this.angle < 225) && (this.angle > 45))
                {
                    this.stepper = 1;
                }
                else if ((this.angle > 225) || (this.angle <= 45))
                {
                    this.stepper = -1;
                };
            }
            else if (this.flyDirect == "r")
            {
                if ((this.angle < 270) && (this.angle > 90))
                {
                    this.stepper = 1;
                }
                else if ((this.angle > 270) || (this.angle <= 90))
                {
                    this.stepper = -1;
                };
            }
            else if (this.flyDirect == "ur")
            {
                if ((this.angle < 315) && (this.angle > 135))
                {
                    this.stepper = 1;
                }
                else if ((this.angle > 315) || (this.angle <= 135))
                {
                    this.stepper = -1;
                };
            }
            else
            {
                this.stepper = 0;
            };
        }

        public function fly(_arg_1:*=null):*
        {
            this.speed = ((-22 - (this.self.auraPercentage * 18)) * ((9 + this.flyTimer) / 18));
            this.controls = this.self.getControls();
            if (this.flyState == 0)
            {
                if ((this.controls.UP != this.startControls[0]) || (this.controls.DOWN != this.startControls[1]) || (this.controls.LEFT != this.startControls[2]) || (this.controls.RIGHT != this.startControls[3]))
                {
                    this.flyState = 1;
                    this.resetStartControls();
                    this.setFlyDirection();
                };
            }
            else if (this.flyState == 1)
            {
                if ((this.controls.UP != this.startControls[0]) || (this.controls.DOWN != this.startControls[1]) || (this.controls.LEFT != this.startControls[2]) || (this.controls.RIGHT != this.startControls[3]))
                {
                    this.resetStartControls();
                    this.setFlyDirection();
                };
            };
            this.stepAngle((this.angleStep * this.stepper));
            this.updateAngle();
            this.self.setXSpeed((this.speed * Math.sin(((this.angle * Math.PI) / 180))));
            if ((this.speed * Math.cos(((this.angle * Math.PI) / 180))) > 1)
            {
                this.self.updateAttackStats({"air_ease":-1});
            }
            else
            {
                this.self.updateAttackStats({"air_ease":0});
            };
            if (this.angle == 90)
            {
                this.self.setYSpeed(0);
            }
            else
            {
                this.self.setYSpeed((this.speed * Math.cos(((this.angle * Math.PI) / 180))));
            };
            if (this.currHand1 != null)
            {
                this.prevHand1 = this.currHand1;
                this.prevHand2 = this.currHand2;
            };
            if (this.self.isFacingRight())
            {
                this.currHand1 = new Point(((this.self.getX() + this.self.getXSpeed()) + this.pos1X[this.getHandFrame()]), ((this.self.getY() + this.self.getYSpeed()) + this.pos1Y[this.getHandFrame()]));
                this.currHand2 = new Point(((this.self.getX() + this.self.getXSpeed()) + this.pos2X[this.getHandFrame()]), ((this.self.getY() + this.self.getYSpeed()) + this.pos2Y[this.getHandFrame()]));
            }
            else
            {
                this.currHand1 = new Point(((this.self.getX() + this.self.getXSpeed()) - this.pos2X[this.getHandFrame()]), ((this.self.getY() + this.self.getYSpeed()) + this.pos2Y[this.getHandFrame()]));
                this.currHand2 = new Point(((this.self.getX() + this.self.getXSpeed()) - this.pos1X[this.getHandFrame()]), ((this.self.getY() + this.self.getYSpeed()) + this.pos1Y[this.getHandFrame()]));
            };
            if (this.prevHand1 == null)
            {
                this.prevHand1 = this.currHand1;
                this.prevHand2 = this.currHand2;
            };
            if (this.self.isFacingRight())
            {
                this.effAng1 = Math.atan2((this.currHand1.y - this.prevHand1.y), (this.currHand1.x - this.prevHand1.x));
                this.effAng2 = Math.atan2((this.currHand2.y - this.prevHand2.y), (this.currHand2.x - this.prevHand2.x));
            }
            else
            {
                this.effAng1 = Math.atan2((this.prevHand1.y - this.currHand1.y), (this.prevHand1.x - this.currHand1.x));
                this.effAng2 = Math.atan2((this.prevHand2.y - this.currHand2.y), (this.prevHand2.x - this.currHand2.x));
            };
            this.effAng1 = ((this.effAng1 * 180) / Math.PI);
            this.effDist1 = Math.sqrt((Math.pow((this.currHand1.x - this.prevHand1.x), 2) + Math.pow((this.currHand1.y - this.prevHand1.y), 2)));
            this.effAng2 = ((this.effAng2 * 180) / Math.PI);
            this.effDist2 = Math.sqrt((Math.pow((this.currHand2.x - this.prevHand2.x), 2) + Math.pow((this.currHand2.y - this.prevHand2.y), 2)));
            if ((this.effDist1 < 200) && (this.effDist2 < 200))
            {
                if (this.self.isFacingRight())
                {
                    this.self.attachEffect("lucario_uspec_trail", {
                        "x":(this.self.flipX(this.pos1X[this.getHandFrame()]) + this.self.getXSpeed()),
                        "y":(this.pos1Y[this.getHandFrame()] + this.self.getYSpeed()),
                        "rotation":this.effAng1,
                        "behind":this.pos1L[this.getHandFrame()],
                        "scaleX":(this.effDist1 / 15)
                    });
                    this.self.attachEffect("lucario_uspec_trail", {
                        "x":(this.self.flipX(this.pos2X[this.getHandFrame()]) + this.self.getXSpeed()),
                        "y":(this.pos2Y[this.getHandFrame()] + this.self.getYSpeed()),
                        "rotation":this.effAng2,
                        "behind":this.pos2L[this.getHandFrame()],
                        "scaleX":(this.effDist2 / 15)
                    });
                }
                else
                {
                    this.self.attachEffect("lucario_uspec_trail", {
                        "x":(this.self.flipX(this.pos2X[this.getHandFrame()]) + this.self.getXSpeed()),
                        "y":(this.pos2Y[this.getHandFrame()] + this.self.getYSpeed()),
                        "rotation":this.effAng1,
                        "behind":this.pos2L[this.getHandFrame()],
                        "scaleX":(this.effDist1 / 15)
                    });
                    this.self.attachEffect("lucario_uspec_trail", {
                        "x":(this.self.flipX(this.pos1X[this.getHandFrame()]) + this.self.getXSpeed()),
                        "y":(this.pos1Y[this.getHandFrame()] + this.self.getYSpeed()),
                        "rotation":this.effAng2,
                        "behind":this.pos1L[this.getHandFrame()],
                        "scaleX":(this.effDist2 / 15)
                    });
                };
            };
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.resetStats);
            this.flyTimer--;
            this.attackAngle = this.angle;
            this.attackAngle += 90;
            if (!this.self.isFacingRight())
            {
                this.attackAngle = (-(this.attackAngle) + 180);
            };
            if (this.attackAngle >= 360)
            {
                this.attackAngle -= 360;
            };
            if (this.attackAngle < 0)
            {
                this.attackAngle += 360;
            };
            if (((this.attackAngle >= 0) && (this.attackAngle < 40)) || ((this.attackAngle >= 330) && (this.attackAngle < 360)))
            {
                this.attackAngle = 40;
            };
            if (this.flyTimer == 2)
            {
                this.self.updateAttackBoxStats(1, {
                    "damage":6,
                    "hitStun":3,
                    "selfHitStun":1,
                    "direction":this.attackAngle,
                    "power":80,
                    "kbConstant":100,
                    "effectSound":"lucario_hit_m",
                    "effect_id":"effect_aurahit_light",
                    "reversableAngle":false,
                    "hasEffect":true
                });
                this.self.updateAuraDamage([1]);
                this.self.refreshAttackID();
            };
            if (this.flyTimer <= 0)
            {
                this.self.updateAttackStats({"air_ease":-1});
                this.resetStats();
                this.self.destroyTimer(this.fly);
                if (!this.groundBelow())
                {
                    this.self.updateAttackStats({
                        "allowControl":true,
                        "allowControlGround":false,
                        "allowFastFall":true
                    });
                    this.self.stancePlayFrame("endAir");
                }
                else if ((this.angle >= 90) && (this.angle <= 270))
                {
                    this.self.setYSpeed(5);
                    this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.land);
                    this.self.stancePlayFrame("endSkid");
                }
                else
                {
                    this.self.toLand();
                };
            };
        }

        public function resetStats(_arg_1:*=null):*
        {
        }

        public function getHandFrame():Number
        {
            return (this.currentFrame - 10) / 2;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.angle = 0;
            this.angleStep = 15;
            this.flyTimer = 9;
            this.startControls = [false, false, false, false];
            this.flyState = 0;
            this.stepper = 0;
            this.flyFrame = 12;
            this.heavyLand = false;
            this.heavyLand2 = false;
            this.angles = [0, 180, 90, 270];
            this.pos1X = [-14.5, -14, -9, -8.5, -6.5, -2.5, -0.5, -4, -8, -9.5, -11.5, -14, -15.5];
            this.pos1Y = [-27.5, -30.5, -31.5, -33, -34.5, -28, -24.5, -22, -16.5, -19, -20.5, -21.5, -26];
            this.pos2X = [11, 11.5, 9, 7, 4.5, 4, 4, 3.5, 3, 5, 6, 11.5, 11];
            this.pos2Y = [-27, -24, -22, -20, -18, -22, -26, -30, -34, -31.5, -29.5, -29, -26];
            this.pos1L = [false, false, false, false, false, false, false, false, false, false, false, true, true];
            this.pos2L = [false, false, true, true, true, true, true, true, true, true, true, true, true];
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAttackBoxStats(1, {
                    "damage":0,
                    "hitStun":0,
                    "selfHitStun":0,
                    "power":0,
                    "kbConstant":0,
                    "effectSound":null,
                    "effect_id":null,
                    "hasEffect":false,
                    "reversableAngle":false
                });
                this.self.updateAuraPaws();
                if (!this.self.isOnGround())
                {
                    this.self.stancePlayFrame("airStart");
                };
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame9():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
            this.controls = this.self.getControls();
            this.angle = 0;
            if ((this.controls.RIGHT && !(this.controls.LEFT) && !(this.controls.UP) && !(this.controls.DOWN)) || (this.controls.RIGHT && !(this.controls.LEFT) && this.controls.UP && this.controls.DOWN))
            {
                this.angle = 270;
                this.self.faceRight();
                this.self.stancePlayFrame(24);
            }
            else if ((this.controls.LEFT && !(this.controls.RIGHT) && !(this.controls.UP) && !(this.controls.DOWN)) || (this.controls.LEFT && !(this.controls.RIGHT) && this.controls.UP && this.controls.DOWN))
            {
                this.angle = 90;
                this.self.faceLeft();
                this.self.stancePlayFrame(24);
            }
            else if ((this.controls.DOWN && !(this.controls.RIGHT) && !(this.controls.LEFT) && !(this.controls.UP)) || (this.controls.DOWN && !(this.controls.UP) && this.controls.LEFT && this.controls.RIGHT))
            {
                if (!this.self.isOnGround())
                {
                    this.angle = 180;
                    this.self.stancePlayFrame(36);
                }
                else if (this.self.isFacingRight())
                {
                    this.angle = 270;
                    this.self.faceRight();
                    this.self.stancePlayFrame(24);
                }
                else
                {
                    this.angle = 90;
                    this.self.faceLeft();
                    this.self.stancePlayFrame(24);
                };
            }
            else if (this.controls.RIGHT && this.controls.UP && !(this.controls.LEFT) && !(this.controls.DOWN))
            {
                this.angle = 315;
                this.self.faceRight();
                this.self.stancePlayFrame(18);
            }
            else if (this.controls.LEFT && this.controls.UP && !(this.controls.RIGHT) && !(this.controls.DOWN))
            {
                this.angle = 45;
                this.self.faceLeft();
                this.self.stancePlayFrame(18);
            }
            else if (this.controls.RIGHT && this.controls.DOWN && !(this.controls.LEFT) && !(this.controls.UP))
            {
                if (!this.self.isOnGround())
                {
                    this.angle = 225;
                    this.self.faceRight();
                    this.self.stancePlayFrame(30);
                }
                else
                {
                    this.angle = 270;
                    this.self.faceRight();
                    this.self.stancePlayFrame(24);
                };
            }
            else if (this.controls.LEFT && this.controls.DOWN && !(this.controls.RIGHT) && !(this.controls.UP))
            {
                if (!this.self.isOnGround())
                {
                    this.angle = 135;
                    this.self.faceLeft();
                    this.self.stancePlayFrame(30);
                }
                else
                {
                    this.angle = 90;
                    this.self.faceLeft();
                    this.self.stancePlayFrame(24);
                };
            };
            if (this.self.isOnGround())
            {
                this.self.attachToGround();
            };
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.resetStartControls();
            this.self.createTimer(1, -1, this.fly);
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame36():*
        {
            this.self.updateAuraPaws();
            this.self.updateAttackBoxStats(1, {
                "damage":0,
                "hitStun":0,
                "selfHitStun":0,
                "power":0,
                "kbConstant":0,
                "effectSound":null,
                "effect_id":null,
                "hasEffect":false,
                "reversableAngle":false
            });
        }

        internal function frame38():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame40():*
        {
            this.heavyLand = true;
        }

        internal function frame46():*
        {
            this.heavyLand2 = true;
        }

        internal function frame51():*
        {
            this.self.toHelpless();
        }

        internal function frame52():*
        {
            this.self.updateAttackStats({
                "canFallOff":true,
                "cancelWhenAirborne":true
            });
            this.self.setYSpeed(0);
            this.self.setXSpeed((this.self.getXSpeed() * 0.7));
            this.self.updateAuraPaws();
            this.self.updateAttackBoxStats(1, {
                "damage":0,
                "hitStun":0,
                "selfHitStun":0,
                "power":0,
                "kbConstant":0,
                "effectSound":null,
                "effect_id":null,
                "hasEffect":false,
                "reversableAngle":false
            });
        }

        internal function frame53():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame61():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame62():*
        {
            this.self.endAttack();
        }

        internal function frame63():*
        {
            this.self.updateAttackStats({
                "canFallOff":true,
                "cancelWhenAirborne":true
            });
            this.self.setYSpeed(0);
            this.self.setXSpeed((this.self.getXSpeed() * 0.6));
            this.self.updateAuraPaws();
        }

        internal function frame65():*
        {
            this.self.attachEffect("ground_bounce");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("lucario_land01");
            };
        }

        internal function frame75():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m");
            }
            else
            {
                this.self.playSound("lucario_step1");
            };
        }

        internal function frame79():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame81():*
        {
            this.self.endAttack();
        }

        internal function frame82():*
        {
            this.self.updateAttackStats({
                "canFallOff":true,
                "cancelWhenAirborne":true
            });
            this.self.setYSpeed(0);
            this.self.setXSpeed((this.self.getXSpeed() * 0.6));
            this.self.updateAuraPaws();
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("lucario_land02");
            };
        }

        internal function frame83():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame105():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame107():*
        {
            this.self.endAttack();
        }

        internal function frame108():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame109():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame116():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
            this.controls = this.self.getControls();
            this.angle = 0;
            if ((this.controls.RIGHT && !(this.controls.LEFT) && !(this.controls.UP) && !(this.controls.DOWN)) || (this.controls.RIGHT && !(this.controls.LEFT) && this.controls.UP && this.controls.DOWN))
            {
                this.angle = 270;
                this.self.faceRight();
                this.self.stancePlayFrame(24);
            }
            else if ((this.controls.LEFT && !(this.controls.RIGHT) && !(this.controls.UP) && !(this.controls.DOWN)) || (this.controls.LEFT && !(this.controls.RIGHT) && this.controls.UP && this.controls.DOWN))
            {
                this.angle = 90;
                this.self.faceLeft();
                this.self.stancePlayFrame(24);
            }
            else if ((this.controls.DOWN && !(this.controls.RIGHT) && !(this.controls.LEFT) && !(this.controls.UP)) || (this.controls.DOWN && !(this.controls.UP) && this.controls.LEFT && this.controls.RIGHT))
            {
                if (!this.self.isOnGround())
                {
                    this.angle = 180;
                    this.self.stancePlayFrame(36);
                }
                else if (this.self.isFacingRight())
                {
                    this.angle = 270;
                    this.self.faceRight();
                    this.self.stancePlayFrame(24);
                }
                else
                {
                    this.angle = 90;
                    this.self.faceLeft();
                    this.self.stancePlayFrame(24);
                };
            }
            else if (this.controls.RIGHT && this.controls.UP && !(this.controls.LEFT) && !(this.controls.DOWN))
            {
                this.angle = 315;
                this.self.faceRight();
                this.self.stancePlayFrame(18);
            }
            else if (this.controls.LEFT && this.controls.UP && !(this.controls.RIGHT) && !(this.controls.DOWN))
            {
                this.angle = 45;
                this.self.faceLeft();
                this.self.stancePlayFrame(18);
            }
            else if (this.controls.RIGHT && this.controls.DOWN && !(this.controls.LEFT) && !(this.controls.UP))
            {
                if (!this.self.isOnGround())
                {
                    this.angle = 225;
                    this.self.faceRight();
                    this.self.stancePlayFrame(30);
                }
                else
                {
                    this.angle = 270;
                    this.self.faceRight();
                    this.self.stancePlayFrame(24);
                };
            }
            else if (this.controls.LEFT && this.controls.DOWN && !(this.controls.RIGHT) && !(this.controls.UP))
            {
                if (!this.self.isOnGround())
                {
                    this.angle = 135;
                    this.self.faceLeft();
                    this.self.stancePlayFrame(30);
                }
                else
                {
                    this.angle = 90;
                    this.self.faceLeft();
                    this.self.stancePlayFrame(24);
                };
            }
            else
            {
                this.self.stancePlayFrame(10);
            };
            if (this.self.isOnGround())
            {
                this.self.attachToGround();
            };
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.resetStartControls();
            this.self.createTimer(1, -1, this.fly);
        }


    }
}

