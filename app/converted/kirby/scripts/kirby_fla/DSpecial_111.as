package kirby_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class DSpecial_111 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var rocktype:String;
        public var kirbyPower:*;
        public var weightDirection:Boolean;
        public var directionMemory:Boolean;
        public var kirbyrock:Number;
        public var tempVar:*;
        public var waiting:*;
        public var myItem:*;

        public function DSpecial_111()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 5, this.frame6, 14, this.frame15, 15, this.frame16, 21, this.frame22, 22, this.frame23, 26, this.frame27, 27, this.frame28, 29, this.frame30, 36, this.frame37, 37, this.frame38, 40, this.frame41, 43, this.frame44, 52, this.frame53, 53, this.frame54, 54, this.frame55, 59, this.frame60, 60, this.frame61, 64, this.frame65, 65, this.frame66, 67, this.frame68, 74, this.frame75, 75, this.frame76, 78, this.frame79, 79, this.frame80, 86, this.frame87, 87, this.frame88, 91, this.frame92, 94, this.frame95, 103, this.frame104, 104, this.frame105, 110, this.frame111, 114, this.frame115, 118, this.frame119, 119, this.frame120, 121, this.frame122, 128, this.frame129, 129, this.frame130, 132, this.frame133, 134, this.frame135, 135, this.frame136, 144, this.frame145, 145, this.frame146, 151, this.frame152, 155, this.frame156, 159, this.frame160, 161, this.frame162, 162, this.frame163, 169, this.frame170, 170, this.frame171, 173, this.frame174, 175, this.frame176, 176, this.frame177, 185, this.frame186, 186, this.frame187, 192, this.frame193, 193, this.frame194, 197, this.frame198, 198, this.frame199, 200, this.frame201, 207, this.frame208, 208, this.frame209, 211, this.frame212, 214, this.frame215, 223, this.frame224, 224, this.frame225, 230, this.frame231, 235, this.frame236, 236, this.frame237, 238, this.frame239, 245, this.frame246, 246, this.frame247, 249, this.frame250, 252, this.frame253, 259, this.frame260, 261, this.frame262, 262, this.frame263, 268, this.frame269, 273, this.frame274, 274, this.frame275, 276, this.frame277, 283, this.frame284, 284, this.frame285, 287, this.frame288, 290, this.frame291, 297, this.frame298, 299, this.frame300, 300, this.frame301, 306, this.frame307, 311, this.frame312, 312, this.frame313, 314, this.frame315, 321, this.frame322, 322, this.frame323, 325, this.frame326);
        }

        public function rockDrop():void
        {
            this.self.setYSpeed(26);
        }

        public function rockTimer():void
        {
            this.waiting = true;
        }

        public function rockSound():void
        {
            this.self.playAttackSound(1);
            this.self.destroyTimer(this.rockSound);
        }

        public function rockEnd():void
        {
            this.self.destroyTimer(this.rockTimer);
            this.self.destroyTimer(this.rockEnd);
            gotoAndStop("finish");
        }

        public function jumpToContinue(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.updateAttackStats({"allowControl":false});
            gotoAndStop("continue");
        }

        public function becomeSolid(_arg_1:Boolean=true):void
        {
        }

        public function landMasterGround(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.landMasterGround);
            this.self.updateAttackBoxStats(1, {
                "damage":3,
                "power":25,
                "direction":75,
                "hitStun":2,
                "selfHitStun":1
            });
            this.self.updateAttackStats({
                "allowControl":true,
                "allowTurn":true
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.rocktype = "normal";
                this.kirbyPower = this.self.getCurrentKirbyPower();
                this.weightDirection = this.self.isFacingRight();
                this.directionMemory = false;
                this.kirbyrock = SSF2API.random();
                this.self.setYSpeed(-8);
                this.self.updateAttackStats({"air_ease":0});
                this.self.createTimer(20, 0, this.rockTimer);
                this.self.createTimer(91, 0, this.rockEnd);
                this.self.createTimer(4, 0, this.rockSound);
            };
        }

        internal function frame2():*
        {
            var _local_1:* = __activation__;
            this.waiting = false;
            this.self.updateAttackStats({"invincible":false});
            this.myItem = this.self.getItem();
            if (this.myItem != null)
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, function ():*
                {
                    myItem.setVisibility(true);
                });
            };
        }

        internal function frame3():*
        {
            this.self.setYSpeed(0);
            if ((this.kirbyrock >= 0.2125) && (this.kirbyrock < 0.425))
            {
                this.rocktype = "weight";
            }
            else if ((this.kirbyrock >= 0.425) && (this.kirbyrock < 0.6375))
            {
                this.rocktype = "panel";
            }
            else if ((this.kirbyrock >= 0.6375) && (this.kirbyrock < 0.85))
            {
                this.rocktype = "spikes";
            }
            else if ((this.kirbyrock >= 0.85) && (this.kirbyrock < 0.98))
            {
                this.rocktype = "thwomp";
            }
            else if ((this.kirbyrock >= 0.98) && (this.kirbyrock < 0.99))
            {
                this.rocktype = "moon";
            }
            else if ((this.kirbyrock >= 0.99) && (this.kirbyrock < 0.9999))
            {
                this.rocktype = "landmaster";
            }
            else if ((this.kirbyrock >= 0.9999) && (this.kirbyrock <= 1))
            {
                this.rocktype = "rare";
            }
            else
            {
                this.rocktype = "normal";
            };
            if (this.rocktype != null)
            {
                this.gotoAndStop(this.rocktype);
            };
        }

        internal function frame6():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(false);
            };
        }

        internal function frame15():*
        {
            this.self.createTimer(1, 0, this.rockDrop);
        }

        internal function frame16():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "invincible":true
            });
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":false});
                this.gotoAndStop("continue");
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.becomeSolid(true);
            stop();
        }

        internal function frame22():*
        {
            gotoAndStop("freeze");
        }

        internal function frame23():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.destroyTimer(this.rockDrop);
            this.tempVar = ("continue_" + this.rocktype);
            if (this.rocktype != "normal")
            {
                if (this.rocktype == "weight")
                {
                    if (!this.weightDirection)
                    {
                        this.tempVar = "continue_weight_left";
                    }
                    else
                    {
                        this.tempVar = "continue_weight_right";
                    };
                };
                gotoAndStop(this.tempVar);
            }
            else
            {
                this.self.updateAttackBoxStats(1, {
                    "power":40,
                    "kbConstant":0,
                    "direction":10
                });
                play();
            };
            SSF2API.getCamera().shake(8);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playAttackSound(3);
            };
        }

        internal function frame27():*
        {
            gotoAndStop("repeat_rock");
        }

        internal function frame28():*
        {
            this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
            this.self.destroyTimer(this.rockTimer);
            this.self.destroyTimer(this.rockEnd);
            this.self.updateAttackStats({"air_ease":0});
            this.becomeSolid(false);
            this.waiting = false;
            this.tempVar = ("finish_" + this.rocktype);
            if (this.rocktype != "normal")
            {
                gotoAndStop(this.tempVar);
            };
        }

        internal function frame30():*
        {
            this.self.updateAttackStats({"invincible":false});
        }

        internal function frame37():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-5);
        }

        internal function frame38():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(true);
            };
        }

        internal function frame41():*
        {
            this.self.endAttack();
        }

        internal function frame44():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(false);
            };
        }

        internal function frame53():*
        {
            this.self.createTimer(1, 0, this.rockDrop);
        }

        internal function frame54():*
        {
            if (this.weightDirection)
            {
                gotoAndStop("weight_right");
            }
            else
            {
                gotoAndStop("weight_left");
            };
        }

        internal function frame55():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "invincible":true
            });
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.isOnGround())
            {
                this.becomeSolid(true);
                this.self.updateAttackStats({"allowControl":false});
                this.gotoAndStop("continue");
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            stop();
        }

        internal function frame60():*
        {
            gotoAndStop("freeze_weight_right");
        }

        internal function frame61():*
        {
            this.self.updateAttackBoxStats(1, {
                "power":40,
                "kbConstant":0,
                "direction":10
            });
        }

        internal function frame65():*
        {
            gotoAndStop("repeat_weight_right");
        }

        internal function frame66():*
        {
            this.becomeSolid(false);
        }

        internal function frame68():*
        {
            this.self.updateAttackStats({"invincible":false});
        }

        internal function frame75():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-5);
        }

        internal function frame76():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(true);
            };
        }

        internal function frame79():*
        {
            this.self.endAttack();
        }

        internal function frame80():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "invincible":true
            });
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.isOnGround())
            {
                this.becomeSolid(true);
                this.self.updateAttackStats({"allowControl":false});
                this.gotoAndStop("continue");
                SSF2API.getCamera().shake(5);
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            stop();
        }

        internal function frame87():*
        {
            gotoAndStop("freeze_weight_left");
        }

        internal function frame88():*
        {
            this.self.updateAttackBoxStats(1, {
                "power":40,
                "kbConstant":0,
                "direction":10
            });
        }

        internal function frame92():*
        {
            gotoAndStop("repeat_weight_left");
        }

        internal function frame95():*
        {
            this.self.updateAttackBoxStats(1, {"direction":75});
            this.self.refreshAttackID();
            if (this.myItem != null)
            {
                this.myItem.setVisibility(false);
            };
        }

        internal function frame104():*
        {
            this.self.createTimer(1, 0, this.rockDrop);
        }

        internal function frame105():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "invincible":true
            });
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":false});
                this.becomeSolid(true);
                this.gotoAndStop("continue");
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            stop();
        }

        internal function frame111():*
        {
            gotoAndStop("freeze_thwomp");
        }

        internal function frame115():*
        {
            this.self.playVoiceSound(4);
            this.self.updateAttackBoxStats(1, {
                "power":40,
                "kbConstant":0,
                "direction":10
            });
        }

        internal function frame119():*
        {
            gotoAndStop("repeat_thwomp");
        }

        internal function frame120():*
        {
            this.becomeSolid(false);
        }

        internal function frame122():*
        {
            this.self.updateAttackStats({"invincible":false});
        }

        internal function frame129():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-5);
        }

        internal function frame130():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(true);
            };
        }

        internal function frame133():*
        {
            this.self.endAttack();
        }

        internal function frame135():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":75,
                "hitStun":3,
                "selfHitStun":3
            });
        }

        internal function frame136():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(false);
            };
        }

        internal function frame145():*
        {
            this.self.createTimer(1, 0, this.rockDrop);
        }

        internal function frame146():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "invincible":true
            });
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.isOnGround())
            {
                this.becomeSolid(true);
                this.self.updateAttackStats({"allowControl":false});
                this.gotoAndStop("continue");
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            stop();
        }

        internal function frame152():*
        {
            gotoAndStop("freeze_panel");
        }

        internal function frame156():*
        {
            this.self.updateAttackBoxStats(1, {
                "power":40,
                "kbConstant":0,
                "direction":10
            });
        }

        internal function frame160():*
        {
            gotoAndStop("repeat_panel");
        }

        internal function frame162():*
        {
            this.becomeSolid(false);
        }

        internal function frame163():*
        {
            this.self.updateAttackStats({"invincible":false});
        }

        internal function frame170():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-5);
        }

        internal function frame171():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(true);
            };
        }

        internal function frame174():*
        {
            this.self.endAttack();
        }

        internal function frame176():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":70,
                "hitStun":2,
                "selfHitStun":2
            });
        }

        internal function frame177():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(false);
            };
        }

        internal function frame186():*
        {
            this.self.createTimer(1, 0, this.rockDrop);
        }

        internal function frame187():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "invincible":true
            });
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":false});
                this.becomeSolid(true);
                this.gotoAndStop("continue");
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            stop();
        }

        internal function frame193():*
        {
            gotoAndStop("freeze_spikes");
        }

        internal function frame194():*
        {
            this.self.updateAttackBoxStats(1, {
                "power":40,
                "kbConstant":0,
                "direction":10
            });
        }

        internal function frame198():*
        {
            gotoAndStop("repeat_spikes");
        }

        internal function frame199():*
        {
            this.becomeSolid(false);
        }

        internal function frame201():*
        {
            this.self.updateAttackStats({"invincible":false});
        }

        internal function frame208():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-5);
        }

        internal function frame209():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(true);
            };
        }

        internal function frame212():*
        {
            this.self.endAttack();
        }

        internal function frame215():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(false);
            };
        }

        internal function frame224():*
        {
            this.self.updateAttackStats({
                "refreshRate":15,
                "air_ease":-1,
                "invincible":true
            });
            this.self.createTimer(1, 0, this.rockDrop);
            stop();
        }

        internal function frame225():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landMasterGround);
            if (this.self.isOnGround())
            {
                this.becomeSolid(true);
            };
        }

        internal function frame231():*
        {
            gotoAndStop("freeze_landmaster");
        }

        internal function frame236():*
        {
            gotoAndStop("repeat_landmaster");
        }

        internal function frame237():*
        {
            this.self.updateAttackStats({
                "refreshRate":15,
                "allowControl":false,
                "allowRun":false,
                "allowTurn":false
            });
            this.becomeSolid(false);
        }

        internal function frame239():*
        {
            this.self.updateAttackStats({"invincible":false});
        }

        internal function frame246():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-5);
        }

        internal function frame247():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(true);
            };
        }

        internal function frame250():*
        {
            this.self.endAttack();
        }

        internal function frame253():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(false);
            };
        }

        internal function frame260():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":90,
                "hitStun":5,
                "selfHitStun":5
            });
            this.self.playVoiceSound(2);
        }

        internal function frame262():*
        {
            this.self.createTimer(1, 0, this.rockDrop);
        }

        internal function frame263():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "invincible":true
            });
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":false});
                this.becomeSolid(true);
                this.gotoAndStop("continue");
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            stop();
        }

        internal function frame269():*
        {
            gotoAndStop("freeze_moon");
        }

        internal function frame274():*
        {
            gotoAndStop("repeat_moon");
        }

        internal function frame275():*
        {
            this.becomeSolid(false);
        }

        internal function frame277():*
        {
            this.self.updateAttackStats({"invincible":false});
        }

        internal function frame284():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-5);
        }

        internal function frame285():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(true);
            };
        }

        internal function frame288():*
        {
            this.self.endAttack();
        }

        internal function frame291():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(false);
            };
        }

        internal function frame298():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":90,
                "hitStun":10,
                "selfHitStun":10
            });
        }

        internal function frame300():*
        {
            this.self.createTimer(1, 0, this.rockDrop);
        }

        internal function frame301():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "invincible":true
            });
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":false});
                this.becomeSolid(true);
                this.gotoAndStop("continue");
            };
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            stop();
        }

        internal function frame307():*
        {
            gotoAndStop("freeze_rare");
        }

        internal function frame312():*
        {
            gotoAndStop("repeat_rare");
        }

        internal function frame313():*
        {
            this.becomeSolid(false);
        }

        internal function frame315():*
        {
            this.self.updateAttackStats({"invincible":false});
        }

        internal function frame322():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-5);
        }

        internal function frame323():*
        {
            if (this.myItem != null)
            {
                this.myItem.setVisibility(true);
            };
        }

        internal function frame326():*
        {
            this.self.endAttack();
        }


    }
}

