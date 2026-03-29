package gameandwatch_fla
{
    import flash.display.MovieClip;
    import flash.display.DisplayObject;

    public dynamic class SSpecial_42 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var number_1:MovieClip;
        public var number_2:MovieClip;
        public var number_3:MovieClip;
        public var number_4:MovieClip;
        public var number_5:MovieClip;
        public var number_6:MovieClip;
        public var number_7:MovieClip;
        public var number_8:MovieClip;
        public var number_9:MovieClip;
        public var self:gameandwatchExt;
        public var selfMC:MovieClip;
        public var number:*;
        public var sounds:Array;
        public var stats:Array;
        public var bleep:*;
        public var i:int;
        public var child:DisplayObject;
        public var childName:String;
        public var cardNumber:*;

        public function SSpecial_42()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 25, this.frame26);
        }

        public function spawnApples(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.spawnApples);
            this.self.generateItem("gnw_apple", false, true, true);
            this.self.generateItem("gnw_apple", false, true, true);
            this.self.generateItem("gnw_apple", false, true, true);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
                this.selfMC = this.self.getStanceMC();
                this.number = SSF2API.randomInteger(1, 9);
                this.self.attachEffect("global_spark", {
                    "x":this.self.flipX(-25),
                    "y":-35
                });
            };
            this.sounds = [];
            this.stats = [{
                "damage":2,
                "hasEffect":false
            }, {
                "damage":4,
                "power":20,
                "kbConstant":30,
                "direction":45,
                "effect_id":"effect_hit2",
                "effectSound":"brawl_kick_s"
            }, {
                "damage":6,
                "power":65,
                "kbConstant":30,
                "direction":145,
                "shieldDamage":80,
                "effect_id":"effect_hit1",
                "effectSound":"brawl_fan"
            }, {
                "damage":8,
                "power":45,
                "kbConstant":30,
                "direction":45,
                "effect_id":"effect_hit2",
                "effectSound":"sw_brawl_hit_S"
            }, {
                "damage":3,
                "power":75,
                "kbConstant":25,
                "direction":75,
                "effect_id":"effect_elechit_light",
                "effectSound":"brawl_zap_s",
                "shock":true
            }, {
                "damage":12,
                "power":35,
                "kbConstant":80,
                "direction":35,
                "effect_id":"effect_firehit_light",
                "effectSound":"brawl_fire_m",
                "burn":true
            }, {
                "damage":14,
                "power":65,
                "kbConstant":20,
                "direction":55,
                "effect_id":"effect_hit2",
                "effectSound":"brawl_punch_m"
            }, {
                "damage":9,
                "power":85,
                "kbConstant":30,
                "direction":85,
                "effect_id":"effect_icehit",
                "effectSound":"freeze_hit",
                "freeze":35
            }, {
                "damage":32,
                "power":110,
                "kbConstant":70,
                "direction":45,
                "hitStun":10,
                "selfHitStun":8,
                "effect_id":"effect_elechit_heavy",
                "effectSound":"bat"
            }];
        }

        internal function frame7():*
        {
        }

        internal function frame8():*
        {
            var _local_1:* = __activation__;
            SSF2API.print(this.number);
            this.bleep = this.self.playSound("snd_se_GW_Wave04_Hi");
            this.i = 0;
            while (this.i < this.selfMC.numChildren)
            {
                this.child = this.selfMC.getChildAt(this.i);
                this.childName = this.child.name;
                if (this.childName.indexOf("number_") >= 0)
                {
                    this.cardNumber = Number(this.childName.substr(7, 1));
                    if (this.cardNumber != this.number)
                    {
                        this.child.visible = false;
                    }
                    else if (!this.self.isFacingRight())
                    {
                        this.child.scaleX = -1;
                    };
                };
                this.i++;
            };
            this.self.updateAttackBoxStats(1, this.stats[(this.number - 1)]);
            if (this.number == 1)
            {
                if (this.self.getCharacterStat("stamina") <= 0)
                {
                    this.self.setDamage((this.self.getDamage() + 12));
                }
                else
                {
                    this.self.setDamage((this.self.getDamage() - 12));
                };
                this.self.throbDamageCounter();
            }
            else if (this.number == 5)
            {
                this.self.createTimer(2, 4, function ():*
                {
                    self.refreshAttackID();
                });
            }
            else if (this.number == 7)
            {
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.spawnApples);
            }
            else if (this.number == 9)
            {
                this.self.attachEffect("gaw_9effect");
                SSF2API.stopSound(this.bleep);
                this.self.playSound("snd_se_GW_Special_S01");
            };
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

