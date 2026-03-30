package lucario_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class AuraSphere_111 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var self:*;
        public var character:*;
        public var metadata:Object;
        public var state:Number;
        public var lifeTimer:Number;
        public var chargeLevel:Number;
        public var auraMultiplier:Number;
        public var auraPercentage:Number;
        public var startPoint:Point;
        public var offsetx:Number;
        public var offsety:Number;
        public var totalOffsetX:Number;
        public var totalOffsetY:Number;
        public var firedStats:Object;
        public var dimmig:*;
        public var effeq:*;

        public function AuraSphere_111()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 8, this.frame9, 9, this.frame10, 11, this.frame12, 12, this.frame13, 14, this.frame15, 15, this.frame16);
        }

        public function refresh(_arg_1:*=null):*
        {
            this.self.refreshAttackID();
        }

        public function update(_arg_1:*=null):*
        {
            if (this.state == 0)
            {
                if (((this.character.getCurrentAnimation() != "b") && (this.character.getCurrentAnimation() != "b_air") && (this.character.getCharacterStat("linkage_id") == "lucario")) || ((this.character.getCurrentAnimation() != "kirby_lucario") && (this.character.getCharacterStat("linkage_id") == "kirby")) || ((this.character.getCharacterStat("linkage_id") != "lucario") && (this.character.getCharacterStat("linkage_id") != "kirby") && (this.character.getCharacterStat("linkage_id") != "chibirobo")))
                {
                    this.self.destroy();
                };
            }
            else if (this.state == 2)
            {
                if (this.lifeTimer > 0)
                {
                    this.startPoint.x += this.self.getXSpeed();
                    this.offsetx = ((this.offsetx + SSF2API.randomInteger(0, 6)) - 3);
                    this.offsety = ((this.offsety + SSF2API.randomInteger(0, 6)) - 3);
                    if ((this.totalOffsetX + this.offsetx) < -4)
                    {
                        this.offsetx = -(this.totalOffsetX + 4);
                        this.totalOffsetX = -4;
                    }
                    else if ((this.totalOffsetX + this.offsetx) > 4)
                    {
                        this.offsetx = -(this.totalOffsetX - 4);
                        this.totalOffsetX = 4;
                    }
                    else
                    {
                        this.totalOffsetX += this.offsetx;
                    };
                    if ((this.totalOffsetY + this.offsety) < -4)
                    {
                        this.offsety = -(this.totalOffsetY + 4);
                        this.totalOffsetY = -4;
                    }
                    else if ((this.totalOffsetY + this.offsety) > 4)
                    {
                        this.offsety = -(this.totalOffsetY - 4);
                        this.totalOffsetY = 4;
                    }
                    else
                    {
                        this.totalOffsetY += this.offsety;
                    };
                    this.self.safeMove(this.offsetx, this.offsety);
                    this.lifeTimer--;
                }
                else
                {
                    this.self.destroy();
                };
            };
        }

        public function spawnTrail(_arg_1:*=null):*
        {
            if (this.self.getGlobalVariable("trailing") == true)
            {
                this.self.attachEffect("effect_lucario_spheretrail", {
                    "behind":true,
                    "scaleX":(this.self.getXSpeed() / 28),
                    "scaleY":(this.self.getScale().y / 3)
                });
            };
        }

        public function despawnEffect(_arg_1:*=null):*
        {
            this.self.attachEffect("effect_lucario_spherepoof", {
                "scaleX":this.self.getScale().x,
                "scaleY":this.self.getScale().y
            });
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.character = null;
            this.metadata = {};
            this.state = 0;
            this.lifeTimer = 36;
            this.chargeLevel = 0;
            this.auraMultiplier = 0;
            this.auraPercentage = 0;
            this.offsetx = 0;
            this.offsety = 0;
            this.totalOffsetX = 0;
            this.totalOffsetY = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                SSF2API.print(this.character.getCharacterStat("linkage_id"));
                if ((this.character.getCharacterStat("linkage_id") == "lucario") || (this.character.getCharacterStat("linkage_id") == "kirby"))
                {
                    this.auraMultiplier = this.character.auraMultiplier;
                    this.auraPercentage = this.character.auraPercentage;
                }
                else if (this.character.getCharacterStat("linkage_id") == "chibirobo")
                {
                    SSF2API.print("WOW!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
                };
                this.self.updateAttackBoxStats(1, {"damage":(this.self.getAttackBoxStat(1, "damage") * this.auraMultiplier)});
                this.self.updateAttackBoxStats(2, {"damage":(this.self.getAttackBoxStat(2, "damage") * this.auraMultiplier)});
                this.self.createTimer(3, -1, this.refresh);
                this.self.createTimer(1, -1, this.update);
            };
        }

        internal function frame7():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame8():*
        {
            if (this.character && ((this.character.getCharacterStat("linkage_id") == "lucario") || (this.character.getCharacterStat("linkage_id") == "kirby")))
            {
                this.chargeLevel = this.character.getStanceMC().localCharge;
            };
            this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.self.destroy);
            this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.self.destroy);
            this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.despawnEffect);
            this.self.updateProjectileStats({"surviveDeathBounds":false});
            this.self.destroyTimer(this.refresh);
            this.spawnTrail();
            this.self.setGlobalVariable("trailing", true);
            this.self.createTimer(4, -1, this.spawnTrail);
            this.self.stancePlayFrame("shot");
            this.state = 1;
        }

        internal function frame9():*
        {
            this.firedStats = {
                "damage":((8 + ((this.chargeLevel / 45) * 12)) * this.auraMultiplier),
                "direction":40,
                "weightKB":0,
                "power":((16 + (20 * this.auraPercentage)) + ((this.chargeLevel / 45) * (14 - (5 * this.auraPercentage)))),
                "kbConstant":(40 + ((this.chargeLevel / 45) * 25)),
                "hitStun":-1,
                "hitLag":-1,
                "reversableAngle":false,
                "priority":0,
                "shieldStunMultiplier":1
            };
            if (this.firedStats.damage < 12)
            {
                this.firedStats.effectSound = "brawl_fire_m";
            }
            else if (this.firedStats.damage < 18)
            {
                this.firedStats.effectSound = "brawl_fire_s";
            }
            else
            {
                this.firedStats.effectSound = "brawl_fire_l";
            };
            this.self.updateAttackBoxStats(1, this.firedStats);
            this.self.updateAttackBoxStats(2, this.firedStats);
            this.self.refreshAttackID();
        }

        internal function frame10():*
        {
            this.self.updateProjectileStats({
                "xspeed":(6.5 + (this.chargeLevel / 3.2)),
                "canBeReversed":true,
                "canBeAbsorbed":true,
                "canBePocketed":true,
                "ghost":false,
                "rideGround":false
            });
            this.startPoint = new Point(this.self.getX(), this.self.getY());
            this.self.setXSpeed((6.5 + (this.chargeLevel / 3.2)), false);
            this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
            this.state = 2;
        }

        internal function frame12():*
        {
            this.self.stancePlayFrame("shotLoop");
        }

        internal function frame13():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.setGlobalVariable("trailing", false);
            this.self.removeEventListener(SSF2Event.PROJ_DESTROYED, this.despawnEffect);
            this.self.destroyTimer(this.update);
        }

        internal function frame15():*
        {
            this.self.stancePlayFrame("susLoop");
        }

        internal function frame16():*
        {
            this.self = SSF2API.getProjectile(this);
            this.lifeTimer = 36;
            this.offsetx = 0;
            this.offsety = 0;
            this.totalOffsetX = 0;
            this.totalOffsetY = 0;
            this.state = 2;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.dimmig = this.self.getAttackBoxStat(1, "damage");
                this.effeq = "";
                if (this.dimmig < 12)
                {
                    this.effeq = "brawl_fire_m";
                }
                else if (this.dimmig < 18)
                {
                    this.effeq = "brawl_fire_s";
                }
                else
                {
                    this.effeq = "brawl_fire_l";
                };
                this.self.updateProjectileStats({
                    "surviveDeathBounds":false,
                    "canBeReversed":true,
                    "canBeAbsorbed":true,
                    "canBePocketed":true,
                    "ghost":false,
                    "rideGround":false
                });
                this.self.updateAttackBoxStats(1, {
                    "direction":40,
                    "weightKB":0,
                    "hitStun":-1,
                    "hitLag":-1,
                    "reversableAngle":false,
                    "priority":0,
                    "shieldStunMultiplier":1,
                    "effectSound":this.effeq
                });
                this.self.updateAttackBoxStats(2, {
                    "direction":40,
                    "weightKB":0,
                    "hitStun":-1,
                    "hitLag":-1,
                    "reversableAngle":false,
                    "priority":0,
                    "shieldStunMultiplier":1,
                    "effectSound":this.effeq
                });
                this.startPoint = new Point(this.self.getX(), this.self.getY());
                this.self.createTimer(1, -1, this.update);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.self.destroy);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.self.destroy);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
                this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.despawnEffect);
                this.self.setGlobalVariable("trailing", true);
                this.self.createTimer(4, -1, this.spawnTrail);
                this.self.stancePlayFrame("shotLoop");
            };
        }


    }
}

