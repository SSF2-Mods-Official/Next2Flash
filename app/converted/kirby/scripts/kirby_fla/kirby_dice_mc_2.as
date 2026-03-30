package kirby_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;
    import flash.events.Event;

    public dynamic class kirby_dice_mc_2 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var dicespinner:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var bounces:*;
        public var timer:*;
        public var rand:*;
        public var p1:Point;
        public var p2:Point;
        public var probabilityLevels:Array;
        public var probabilities:Array;
        public var sounds:Array;
        public var stats:Array;
        public var i:*;
        public var j:*;
        public var character:*;

        public function kirby_dice_mc_2()
        {
            super();
            addFrameScript(0, this.frame1, 19, this.frame20, 20, this.frame21, 24, this.frame25, 26, this.frame27, 27, this.frame28);
        }

        public function spinVisual(_arg_1:*=null):*
        {
            this.timer--;
            this.dicespinner.rotation += (this.self.getXSpeed() * Math.abs((this.self.getXSpeed() * 0.5)));
            if (this.timer <= 0)
            {
                this.self.destroyTimer(this.spinVisual);
                this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.pop);
                this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.pop);
                this.self.removeEventListener(SSF2Event.HIT_WALL, this.wallBounce);
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundBounce);
                this.self.removeEventListener(SSF2Event.PROJ_COLLIDE, this.checkPop);
                this.self.destroy();
            };
        }

        public function wallBounce(_arg_1:Event=null):void
        {
            if (this.checkForSlope() == "wall")
            {
                this.self.setXSpeed((-1 * this.self.getXSpeed()));
                this.self.setYSpeed((-(this.self.getYSpeed()) * 0.5));
            }
            else
            {
                this.self.setXSpeed(-(this.flipX(4.5)));
                this.self.setYSpeed(-6);
                this.self.attachEffect("effect_land");
                this.timer += 20;
            };
            this.self.playSound("waluigi_swing_m");
        }

        public function groundBounce(_arg_1:Event=null):void
        {
            if (this.bounces < 1)
            {
                if (this.checkForSlope() == "up")
                {
                    this.self.setXSpeed(-(this.flipX(4.5)));
                    this.self.setYSpeed(-6);
                    this.timer += 20;
                }
                else if (this.checkForSlope() == "down")
                {
                    this.bounces++;
                    this.self.setYSpeed((-(this.self.getYSpeed()) * 0.5));
                }
                else
                {
                    this.bounces++;
                    this.self.setXSpeed((this.self.getXSpeed() * 0.6));
                    this.self.setYSpeed((-(this.self.getYSpeed()) * 0.8));
                };
                this.self.attachEffect("effect_land");
                this.self.playSound("waluigi_swing_m");
            }
            else
            {
                this.pop();
            };
        }

        public function pop(_arg_1:*=null):*
        {
            this.self.destroyTimer(this.spinVisual);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.pop);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.pop);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.wallBounce);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundBounce);
            this.self.removeEventListener(SSF2Event.PROJ_COLLIDE, this.checkPop);
            this.self.stancePlayFrame("pop");
        }

        public function checkPop(_arg_1:*=null):*
        {
            if ((_arg_1 != null) && (_arg_1.data.opponent.getType() == "SSF2Target"))
            {
                _arg_1.data.opponent.breakTarget();
                this.pop();
            };
        }

        public function checkForSlope():String
        {
            if (!SSF2API.hitTestGround(this.self.getX(), (this.self.getY() + 5)))
            {
                return "wall";
            }
            else
            if (SSF2API.hitTestGround((this.self.getX() + this.flipX(16)), this.self.getY()) && !(SSF2API.hitTestGround((this.self.getX() + this.flipX(-16)), this.self.getY())))
            {
                return "up";
            }
            else
            if (SSF2API.hitTestGround((this.self.getX() + this.flipX(-16)), this.self.getY()) && !(SSF2API.hitTestGround((this.self.getX() + this.flipX(16)), this.self.getY())))
            {
                return "down";
            }
            else
            {
            return "flat";
            };
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.getXSpeed() > 0)
            {
                return _arg_1;
            };
            return -(_arg_1);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.bounces = 0;
            this.timer = 65;
            this.p1 = new Point();
            this.p2 = new Point();
            this.probabilityLevels = [4, 4, 4, 4, 3, 1];
            this.probabilities = [];
            this.sounds = [["trophycapture", "waluigi_horn"], ["waluigi_wind", "throw_release"], ["waluigi_poison"], ["smallshock"], ["waluigi_bury"], ["bombexplode", "brawl_almostdied", "waluigi_bighorn"]];
            this.stats = [{
                "hasEffect":true,
                "effectSound":"brawl_punch_s",
                "effect_id":"effect_hit3",
                "damage":3,
                "hitStun":2,
                "direction":90,
                "power":20,
                "kbConstant":0,
                "hitLag":-1
            }, {
                "hasEffect":false,
                "effectSound":null,
                "effect_id":null,
                "damage":0,
                "hitStun":0,
                "direction":30,
                "power":110,
                "kbConstant":0,
                "hitLag":-1,
                "stackKnockback":false
            }, {
                "hasEffect":true,
                "effectSound":null,
                "effect_id":null,
                "damage":0,
                "hitStun":4,
                "direction":90,
                "power":30,
                "kbConstant":5,
                "hitLag":-1,
                "poison":1,
                "poisonInterval":10,
                "poisonLength":120
            }, {
                "hasEffect":true,
                "effectSound":"brawl_zap_m",
                "effect_id":"effect_elechit_light",
                "damage":5,
                "hitStun":0,
                "direction":70,
                "power":35,
                "kbConstant":60,
                "hitLag":-1,
                "shock":true,
                "paralysis":20
            }, {
                "hasEffect":true,
                "effectSound":"brawl_kick_l",
                "effect_id":"effect_heavyHit",
                "damage":8,
                "hitStun":4,
                "direction":270,
                "power":36,
                "kbConstant":50,
                "hitLag":-1,
                "pitfall":25
            }, {
                "hasEffect":true,
                "effectSound":"brawl_fire_l",
                "effect_id":"effect_firehit_heavy",
                "damage":20,
                "hitStun":12,
                "selfHitStun":10,
                "direction":45,
                "power":75,
                "kbConstant":80,
                "hitLag":-1,
                "burn":true
            }];
            if (SSF2API.isReady() && this.self)
            {
                this.i = 0;
                while (this.i < this.probabilityLevels.length)
                {
                    this.j = 0;
                    while (this.j < this.probabilityLevels[this.i])
                    {
                        this.probabilities.push(this.i);
                        this.j++;
                    };
                    this.i++;
                };
                this.self.faceRight();
                this.character = this.self.getOwner();
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.pop);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.pop);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wallBounce);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.groundBounce);
                this.self.addEventListener(SSF2Event.PROJ_COLLIDE, this.checkPop);
                this.self.createTimer(1, -1, this.spinVisual);
            };
        }

        internal function frame20():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame21():*
        {
            this.self.playSound("waluigi_clap");
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.updateProjectileStats({
                "canBePocketed":false,
                "gravity":0
            });
            this.rand = this.probabilities[SSF2API.randomInteger(0, (this.probabilities.length - 1))];
            this.self.attachEffect(("effect_waluigi_" + (this.rand + 1).toString()), {
                "flip":false,
                "y":-20
            });
            this.i = 0;
            while (this.i < this.sounds[this.rand].length)
            {
                this.self.playSound(this.sounds[this.rand][this.i]);
                this.i++;
            };
            this.self.updateAttackBoxStats(1, this.stats[this.rand]);
            this.self.refreshAttackID();
        }

        internal function frame25():*
        {
            this.self.destroy();
        }

        internal function frame27():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame28():*
        {
            this.self = SSF2API.getProjectile(this);
            this.bounces = 0;
            this.timer = 65;
            this.p1 = new Point();
            this.p2 = new Point();
            this.probabilityLevels = [4, 4, 4, 4, 3, 1];
            this.probabilities = [];
            this.sounds = [["trophycapture", "waluigi_horn"], ["waluigi_wind", "throw_release"], ["waluigi_poison"], ["smallshock"], ["waluigi_bury"], ["bombexplode", "brawl_almostdied", "waluigi_bighorn"]];
            this.stats = [{
                "hasEffect":true,
                "effectSound":"brawl_punch_s",
                "effect_id":"effect_hit3",
                "damage":3,
                "hitStun":2,
                "direction":90,
                "power":20,
                "kbConstant":0,
                "hitLag":-1
            }, {
                "hasEffect":false,
                "effectSound":null,
                "effect_id":null,
                "damage":0,
                "hitStun":0,
                "direction":30,
                "power":110,
                "kbConstant":0,
                "hitLag":-1,
                "stackKnockback":false
            }, {
                "hasEffect":true,
                "effectSound":null,
                "effect_id":null,
                "damage":0,
                "hitStun":4,
                "direction":90,
                "power":30,
                "kbConstant":5,
                "hitLag":-1,
                "poison":1,
                "poisonInterval":10,
                "poisonLength":120
            }, {
                "hasEffect":true,
                "effectSound":"brawl_zap_m",
                "effect_id":"effect_elechit_light",
                "damage":5,
                "hitStun":0,
                "direction":70,
                "power":35,
                "kbConstant":60,
                "hitLag":-1,
                "shock":true,
                "paralysis":20
            }, {
                "hasEffect":true,
                "effectSound":"brawl_kick_l",
                "effect_id":"effect_heavyHit",
                "damage":8,
                "hitStun":4,
                "direction":270,
                "power":36,
                "kbConstant":50,
                "hitLag":-1,
                "pitfall":25
            }, {
                "hasEffect":true,
                "effectSound":"brawl_fire_l",
                "effect_id":"effect_firehit_heavy",
                "damage":20,
                "hitStun":12,
                "selfHitStun":10,
                "direction":45,
                "power":75,
                "kbConstant":80,
                "hitLag":-1,
                "burn":true
            }];
            if (SSF2API.isReady() && this.self)
            {
                this.i = 0;
                while (this.i < this.probabilityLevels.length)
                {
                    this.j = 0;
                    while (this.j < this.probabilityLevels[this.i])
                    {
                        this.probabilities.push(this.i);
                        this.j++;
                    };
                    this.i++;
                };
                this.self.faceRight();
                this.character = this.self.getOwner();
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.pop);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.pop);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wallBounce);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.groundBounce);
                this.self.addEventListener(SSF2Event.PROJ_COLLIDE, this.checkPop);
                this.self.createTimer(1, -1, this.spinVisual);
                this.self.stancePlayFrame("loop");
            };
        }


    }
}

