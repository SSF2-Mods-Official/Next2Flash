// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_specialU_50

package fox_fla
{
    import flash.display.MovieClip;
    import flash.display.*;
    import flash.geom.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class fox_specialU_50 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var speed:Number;
        public var afterDecay:Number;
        public var isOnGround:*;
        public var proj:*;
        public var closestLedge:*;
        public var closestLedgeDistance:Number;
        public var ledges:Array;
        public var i:int;
        public var ledge:MovieClip;
        public var xDiff:Number;
        public var yDiff:Number;
        public var distance:Number;
        public var xDist:Number;
        public var yDist:Number;
        public var angle:Number;
        public var randomNumber:Number;
        public var controls:Object;
        public var isFacingRight:Boolean;
        public var north:Number;
        public var east:Number;
        public var up:*;
        public var down:*;
        public var right:*;
        public var left:*;
        public var flip:*;

        public function fox_specialU_50()
        {
            addFrameScript(0, this.frame1, 9, this.frame10, 21, this.frame22, 22, this.frame23, 42, this.frame43, 47, this.frame48, 56, this.frame57, 64, this.frame65, 65, this.frame66, 70, this.frame71, 79, this.frame80, 80, this.frame81, 85, this.frame86, 93, this.frame94, 94, this.frame95, 95, this.frame96, 106, this.frame107, 109, this.frame110, 110, this.frame111, 121, this.frame122, 124, this.frame125, 125, this.frame126, 130, this.frame131, 139, this.frame140, 140, this.frame141, 145, this.frame146, 153, this.frame154, 154, this.frame155, 155, this.frame156, 166, this.frame167, 169, this.frame170, 170, this.frame171, 175, this.frame176, 178, this.frame179, 179, this.frame180, 180, this.frame181, 185, this.frame186, 188, this.frame189, 189, this.frame190);
        }

        public function landing(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.landing);
            SSF2API.print("landing");
            if (this.flip)
            {
                this.self.flip();
            };
            this.self.toHeavyLand();
        }

        public function afterImage():void
        {
            this.self.attachEffect("firefoxTrail", {"y":-19});
        }

        public function fire(_arg_1:*=null):void
        {
            if (this.up)
            {
                this.self.setYSpeed(-(this.speed));
            };
            if (this.down)
            {
                this.self.setYSpeed(this.speed);
            };
            if (this.left)
            {
                this.self.setXSpeed(-(this.speed));
            };
            if (this.right)
            {
                this.self.setXSpeed(this.speed);
            };
        }

        public function bounce(_arg_1:*=null):void
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            if (((this.currentLabel == "takeoffSE") || (this.currentLabel == "takeoffSW")))
            {
                this.self.stancePlayFrame("bounceEast");
            }
            else
            {
                if (this.currentLabel == "takeoffS")
                {
                    this.self.stancePlayFrame("bounceNorth");
                };
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                this.speed = 16.5;
                this.afterDecay = -0.5;
                this.isOnGround = this.self.isOnGround();
                this.self.updateAttackStats({"allowControl":false});
                this.self.playAttackSound(1);
                this.self.setYSpeed((this.self.getYSpeed() * 0.5));
                this.self.setXSpeed((this.self.getXSpeed() * 0.65));
                this.self.fireProjectile("fox_uspecProj");
                this.proj = this.self.getCurrentProjectile();
            };
        }

        internal function frame10():*
        {
        }

        internal function frame22():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "refreshRate":30
            });
            this.self.updateAttackBoxStats(1, {"kbConstant":60});
            if ((((this.self.isCPU()) && (this.self.getCPULevel() >= 7)) && ((((this.self.inLowerLeftWarningBounds()) || (this.self.inLowerRightWarningBounds())) || (this.self.inUpperLeftWarningBounds())) || (this.self.inUpperRightWarningBounds()))))
            {
                this.closestLedgeDistance = Number.MAX_VALUE;
                this.ledges = SSF2API.getStage().getLedges();
                this.i = 0;
                while (this.i < this.ledges.length)
                {
                    this.ledge = (this.ledges[this.i] as MovieClip);
                    this.xDiff = (this.ledge.x - this.self.getX());
                    this.yDiff = (-1 * (this.ledge.y - this.self.getY()));
                    this.distance = ((this.xDiff * this.xDiff) + (this.yDiff * this.yDiff));
                    if (this.distance <= this.closestLedgeDistance)
                    {
                        this.closestLedge = this.ledge;
                        this.closestLedgeDistance = this.distance;
                    };
                    this.i++;
                };
                if (this.closestLedge != null)
                {
                    SSF2API.print("ledge found!");
                    this.xDist = (this.closestLedge.x - this.self.getX());
                    this.yDist = (-1 * (this.closestLedge.y - this.self.getY()));
                    SSF2API.print(("x Difference: " + this.xDist.toString()));
                    SSF2API.print(("y Difference: " + this.yDist.toString()));
                    this.angle = SSF2Utils.toDegrees(Math.atan2(this.yDist, this.xDist));
                    SSF2API.print(this.angle.toString());
                    if (((this.angle >= 0) && (this.angle <= 45)))
                    {
                        if (SSF2API.random() < 0.8)
                        {
                            this.self.importCPUControls([0x0900, 30]);
                            SSF2API.print("aiming up-right");
                        }
                        else
                        {
                            this.self.importCPUControls([0x0800, 30]);
                            SSF2API.print("aiming up");
                        };
                    }
                    else
                    {
                        if (((this.angle >= 45) && (this.angle <= 135)))
                        {
                            this.self.importCPUControls([0x0800, 30]);
                            SSF2API.print("aiming up");
                        }
                        else
                        {
                            if (((this.angle >= 135) && (this.angle <= 180)))
                            {
                                if (SSF2API.random() < 0.8)
                                {
                                    this.self.importCPUControls([0x0A00, 30]);
                                    SSF2API.print("aiming up-left");
                                }
                                else
                                {
                                    this.self.importCPUControls([0x0200, 30]);
                                    SSF2API.print("aiming left");
                                };
                            }
                            else
                            {
                                if (((this.angle >= -180) && (this.angle <= -135)))
                                {
                                    this.randomNumber = SSF2API.random();
                                    if (this.randomNumber < 0.8)
                                    {
                                        this.self.importCPUControls([0x0200, 30]);
                                        SSF2API.print("aiming left");
                                    }
                                    else
                                    {
                                        if (this.randomNumber < 0.9)
                                        {
                                            this.self.importCPUControls([0x0A00, 30]);
                                            SSF2API.print("aiming up-left");
                                        }
                                        else
                                        {
                                            this.self.importCPUControls([0x0800, 30]);
                                            SSF2API.print("aiming up");
                                        };
                                    };
                                }
                                else
                                {
                                    if (((this.angle > -135) && (this.angle <= -90)))
                                    {
                                        this.randomNumber = SSF2API.random();
                                        if (this.randomNumber < 0.8)
                                        {
                                            this.self.importCPUControls([0x0200, 30]);
                                            SSF2API.print("aiming left");
                                        }
                                        else
                                        {
                                            if (this.randomNumber < 0.9)
                                            {
                                                this.self.importCPUControls([0x0A00, 30]);
                                                SSF2API.print("aiming up-left");
                                            }
                                            else
                                            {
                                                this.self.importCPUControls([0x0800, 30]);
                                                SSF2API.print("aiming up");
                                            };
                                        };
                                    }
                                    else
                                    {
                                        this.randomNumber = SSF2API.random();
                                        if (this.randomNumber < 0.8)
                                        {
                                            this.self.importCPUControls([0x0100, 30]);
                                            SSF2API.print("aiming right");
                                        }
                                        else
                                        {
                                            if (this.randomNumber < 0.9)
                                            {
                                                this.self.importCPUControls([0x0900, 30]);
                                                SSF2API.print("aiming up-right");
                                            }
                                            else
                                            {
                                                this.self.importCPUControls([0x0800, 30]);
                                                SSF2API.print("aiming up");
                                            };
                                        };
                                    };
                                };
                            };
                        };
                    };
                };
                this.self.addEventListener(SSF2Event.STATE_CHANGE, function ():*
                {
                    self.resetCPUControls();
                });
                this.self.addEventListener(SSF2Event.CHAR_ATTACK_COMPLETE, function ():*
                {
                    self.resetCPUControls();
                });
            };
        }

        internal function frame23():*
        {
            this.controls = this.self.getControls();
            this.isFacingRight = this.self.isFacingRight();
            this.north = 0;
            this.east = 0;
            this.up = false;
            this.down = false;
            this.right = false;
            this.left = false;
            this.flip = false;
            this.self.updateAttackBoxStats(1, {
                "power":60,
                "kbConstant":60,
                "hitStun":4,
                "direction":90,
                "selfHitStun":2,
                "damage":10,
                "effect_id":"effect_firehit_heavy"
            });
            this.self.refreshAttackID();
            this.self.unnattachFromGround();
            this.self.createTimer(3, 15, this.afterImage);
            this.controls = this.self.getControls();
            if (this.controls.UP)
            {
                this.up = true;
            };
            if (this.controls.DOWN)
            {
                this.down = true;
            };
            if (this.controls.LEFT)
            {
                this.left = true;
            };
            if (this.controls.RIGHT)
            {
                this.right = true;
            };
            if (((this.isOnGround) && (this.down)))
            {
                this.down = false;
            };
            if (((((this.up) && (this.down)) || ((this.left) && (this.right))) || ((((!(this.up)) && (!(this.down))) && (!(this.left))) && (!(this.right)))))
            {
                this.up = true;
                this.left = false;
                this.right = false;
                this.down = false;
            };
            if (((((this.left) && (!(this.right))) && (!(this.up))) && (!(this.down))))
            {
                this.self.updateAttackStats({"air_ease":0});
                if (this.isFacingRight)
                {
                    this.flip = true;
                    this.self.stancePlayFrame("takeoffW");
                }
                else
                {
                    this.self.stancePlayFrame("takeoffE");
                };
            };
            if (((((this.right) && (!(this.left))) && (!(this.up))) && (!(this.down))))
            {
                this.self.updateAttackStats({"air_ease":0});
                if (this.isFacingRight)
                {
                    this.self.stancePlayFrame("takeoffE");
                }
                else
                {
                    this.flip = true;
                    this.self.stancePlayFrame("takeoffW");
                };
            };
            if (((((this.up) && (!(this.right))) && (!(this.left))) && (!(this.down))))
            {
                this.self.stancePlayFrame("takeoffN");
            };
            if (((((this.down) && (!(this.right))) && (!(this.left))) && (!(this.up))))
            {
                this.self.stancePlayFrame("takeoffS");
            };
            if (((((this.left) && (!(this.right))) && (this.up)) && (!(this.down))))
            {
                if (this.isFacingRight)
                {
                    this.flip = true;
                    this.self.stancePlayFrame("takeoffNW");
                }
                else
                {
                    this.self.stancePlayFrame("takeoffNE");
                };
            };
            if (((((this.right) && (!(this.left))) && (this.up)) && (!(this.down))))
            {
                if (this.isFacingRight)
                {
                    this.self.stancePlayFrame("takeoffNE");
                }
                else
                {
                    this.flip = true;
                    this.self.stancePlayFrame("takeoffNW");
                };
            };
            if (((((this.left) && (!(this.right))) && (!(this.up))) && (this.down)))
            {
                if (this.isFacingRight)
                {
                    this.flip = true;
                    this.self.stancePlayFrame("takeoffSW");
                }
                else
                {
                    this.self.stancePlayFrame("takeoffSE");
                };
            };
            if (((((this.right) && (!(this.left))) && (!(this.up))) && (this.down)))
            {
                if (this.isFacingRight)
                {
                    this.self.stancePlayFrame("takeoffSE");
                }
                else
                {
                    this.flip = true;
                    this.self.stancePlayFrame("takeoffSW");
                };
            };
            if ((((((this.up) && (this.right)) || ((this.up) && (this.left))) || ((this.down) && (this.right))) || ((this.down) && (this.left))))
            {
                this.speed = (this.speed / 1.2);
            };
            this.self.createTimer(1, 14, this.fire);
        }

        internal function frame43():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "effectSound":"brawl_fire_l"
            });
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.resetMovement();
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("up");
            };
        }

        internal function frame48():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame57():*
        {
            this.self.destroyTimer(this.afterImage);
            this.self.destroyTimer(this.fire);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.landing);
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":6,
                "xSpeedDecayAir":0.25,
                "xSpeedCap":5
            });
            if (!this.self.isOnGround())
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
            }
            else
            {
                this.self.toHeavyLand();
            };
            if (this.flip)
            {
                this.flip = false;
                this.self.flip();
            };
        }

        internal function frame65():*
        {
            if (this.self.isOnGround())
            {
                this.landing();
            }
            else
            {
                this.self.setGlobalVariable("usedUpB", true);
                this.self.toHelpless();
            };
        }

        internal function frame66():*
        {
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "effectSound":"brawl_fire_l"
            });
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("upright");
            };
        }

        internal function frame71():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame80():*
        {
            this.self.stancePlayFrame("ending");
        }

        internal function frame81():*
        {
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "effectSound":"brawl_fire_l"
            });
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("right");
            };
        }

        internal function frame86():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame94():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame95():*
        {
            this.self.stancePlayFrame("ending");
        }

        internal function frame96():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "effectSound":"brawl_fire_l"
            });
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("downright");
            };
        }

        internal function frame107():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame110():*
        {
            this.self.stancePlayFrame("ending");
        }

        internal function frame111():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "effectSound":"brawl_fire_l"
            });
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("down");
            };
        }

        internal function frame122():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame125():*
        {
            this.self.stancePlayFrame("ending");
        }

        internal function frame126():*
        {
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "effectSound":"brawl_fire_l"
            });
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("upleft");
            };
        }

        internal function frame131():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame140():*
        {
            this.self.stancePlayFrame("ending");
        }

        internal function frame141():*
        {
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "effectSound":"brawl_fire_l"
            });
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("left");
            };
        }

        internal function frame146():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame154():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame155():*
        {
            this.self.stancePlayFrame("ending");
        }

        internal function frame156():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.updateAttackStats({"refreshRate":9999});
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.updateAttackBoxStats(1, {
                "damage":14,
                "effectSound":"brawl_fire_l"
            });
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("downleft");
            };
        }

        internal function frame167():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame170():*
        {
            this.self.stancePlayFrame("ending");
        }

        internal function frame171():*
        {
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":-1
            });
            this.self.unnattachFromGround();
            this.self.setYSpeed(-16);
            this.self.destroyTimer(this.afterImage);
            this.self.destroyTimer(this.fire);
            if (this.flip)
            {
                this.self.flip();
            };
            if (((this.flip) && (this.self.isFacingRight())))
            {
                this.self.setXSpeed(10);
            }
            else
            {
                if (((this.flip) && (!(this.self.isFacingRight()))))
                {
                    this.self.setXSpeed(-10);
                }
                else
                {
                    this.self.setXSpeed(10, false);
                };
            };
            this.flip = false;
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("kill");
            };
        }

        internal function frame176():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame179():*
        {
            if (this.self.isOnGround())
            {
                this.landing();
            }
            else
            {
                this.self.setGlobalVariable("usedUpB", true);
                this.self.toHelpless();
            };
        }

        internal function frame180():*
        {
            this.self.toHelpless();
        }

        internal function frame181():*
        {
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":-1,
                "xSpeedDecayAir":this.afterDecay
            });
            this.self.unnattachFromGround();
            this.self.setYSpeed(-16);
            this.self.destroyTimer(this.fire);
            this.self.destroyTimer(this.afterImage);
            if (this.flip)
            {
                this.flip = false;
                this.self.flip();
            };
            if (((this.proj) && (!(this.proj.isDisposed()))))
            {
                this.proj.stancePlayFrame("kill");
            };
        }

        internal function frame186():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landing);
        }

        internal function frame189():*
        {
            if (this.self.isOnGround())
            {
                this.landing();
            }
            else
            {
                this.self.setGlobalVariable("usedUpB", true);
                this.self.toHelpless();
            };
        }

        internal function frame190():*
        {
            this.self.toHelpless();
        }


    }
}//package fox_fla

