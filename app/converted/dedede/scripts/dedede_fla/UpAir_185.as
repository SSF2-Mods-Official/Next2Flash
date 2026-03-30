package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class UpAir_185 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var kb:*;
        public var angle:*;
        public var xDis:*;
        public var yDis:*;
        public var distance:*;
        public var offset:*;
        public var kbc:*;
        public var power:*;
        public var wkb:*;
        public var landingHit:Boolean;
        public var playsound:Number;
        public var audio:Number;

        public function UpAir_185()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 5, this.frame6, 7, this.frame8, 9, this.frame10, 11, this.frame12, 12, this.frame13, 20, this.frame21, 22, this.frame23, 23, this.frame24, 29, this.frame30);
        }

        public function moveOpp(_arg_1:*=null):*
        {
            var _local_2:* = _arg_1.data.receiver;
            var _local_3:* = _local_2.getType().slice(4);
            var _local_4:* = (("get" + _local_3) + "Stat");
            if (((_local_3 == "Character") && this.hit(_local_2)) || (_local_3 == "Item") || (_local_3 == "Enemy"))
            {
                var _local_5:* = _local_2;
                if (_local_2[_local_4]._local_5("canReceiveKnockback"))
                {
                    this.xDis = ((this.self.getX() + (this.self.getXSpeed() * 2)) - _local_2.getX());
                    _local_5 = _local_2;
                    this.yDis = ((((this.self.getY() - 65) + (this.self.getYSpeed() * 2)) - _local_2.getY()) - (this.offset * _local_2[_local_4]._local_5("gravity")));
                    _local_5 = _local_2;
                    this.yDis = (-(this.yDis) * _local_2[_local_4]._local_5("gravity"));
                    if ((this.self.getY() - 10) < _local_2.getY())
                    {
                        if (_local_2.isOnGround())
                        {
                            this.xDis /= 2.5;
                        };
                        this.yDis /= 2.5;
                    };
                    this.distance = Math.sqrt((Math.pow(Math.abs(this.xDis), 2) + Math.pow(Math.abs(this.yDis), 2)));
                    this.kbc = 0;
                    this.power = (30 + (this.distance * 0.8));
                    this.wkb = 100;
                    _local_5 = _local_2;
                    this.kb = SSF2API.calculateKnockback(this.kbc, this.power, this.wkb, this.self.getAttackBoxStat(1, "damage"), _local_2.getDamage(), _local_2[_local_4]._local_5("weight1"), false);
                    this.angle = Math.atan2(this.yDis, this.xDis);
                    this.angle = ((this.angle * 180) / Math.PI);
                    _local_2.resetKnockback();
                    _local_2.applyKnockback(this.kb, this.angle);
                    _local_2.forceHitStun(2);
                };
            };
        }

        public function hit(_arg_1:*):Boolean
        {
            if ((_arg_1.getState() == 14) || (_arg_1.getState() == 26) || (_arg_1.getState() == 27))
            {
                return true;
            };
            return false;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.offset = 15;
            this.kbc = 0;
            this.power = 40;
            this.landingHit = true;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.moveOpp);
            };
        }

        internal function frame4():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame5():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_uair");
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
        }

        internal function frame6():*
        {
            this.self.refreshAttackID();
        }

        internal function frame8():*
        {
            this.self.refreshAttackID();
        }

        internal function frame10():*
        {
            this.self.refreshAttackID();
        }

        internal function frame12():*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.moveOpp);
            this.self.updateAttackBoxStats(1, {
                "damage":6,
                "hitLag":-1,
                "hitStun":-1,
                "selfHitStun":-1,
                "effectSound":"ssf2_snd_sfx_dedede_hit_m",
                "effect_id":"effect_heavyHit",
                "direction":90,
                "power":50,
                "kbConstant":150,
                "stackKnockback":false
            });
            this.self.updateAttackBoxStats(2, {
                "damage":6,
                "hitLag":-1,
                "hitStun":-1,
                "selfHitStun":-1,
                "effectSound":"ssf2_snd_sfx_dedede_hit_m",
                "effect_id":"effect_heavyHit",
                "direction":90,
                "power":50,
                "kbConstant":150,
                "stackKnockback":false
            });
            this.self.refreshAttackID();
        }

        internal function frame13():*
        {
            this.landingHit = false;
        }

        internal function frame21():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }

        internal function frame24():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_dedede_landHeavy");
                };
            };
            SSF2API.getCamera().shake(3);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.moveOpp);
            if (this.landingHit)
            {
                this.self.updateAttackBoxStats(1, {
                    "damage":2,
                    "hitLag":-1,
                    "hitStun":3,
                    "selfHitStun":1,
                    "effectSound":"dedede_hammerhitS",
                    "effect_id":"effect_hit2",
                    "direction":90,
                    "power":50,
                    "kbConstant":60
                });
                this.self.updateAttackBoxStats(2, {
                    "damage":2,
                    "hitLag":-1,
                    "hitStun":3,
                    "selfHitStun":1,
                    "effectSound":"dedede_hammerhitS",
                    "effect_id":"effect_hit2",
                    "direction":90,
                    "power":50,
                    "kbConstant":60
                });
                this.self.refreshAttackID();
            };
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }


    }
}

