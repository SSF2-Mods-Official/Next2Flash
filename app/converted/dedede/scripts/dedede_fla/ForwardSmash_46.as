package dedede_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class ForwardSmash_46 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var xframe:String;

        public function ForwardSmash_46()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9, 10, this.frame11, 12, this.frame13, 14, this.frame15, 15, this.frame16, 55, this.frame56, 56, this.frame57, 58, this.frame59, 59, this.frame60, 60, this.frame61, 61, this.frame62, 62, this.frame63, 63, this.frame64, 66, this.frame67, 74, this.frame75, 77, this.frame78, 79, this.frame80, 81, this.frame82);
        }

        public function shift(_arg_1:Number):*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(_arg_1)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(_arg_1)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(_arg_1), 0);
            };
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(9),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame4():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame9():*
        {
            this.shift(5);
        }

        internal function frame11():*
        {
            this.shift(5);
        }

        internal function frame13():*
        {
            this.shift(4);
        }

        internal function frame15():*
        {
            this.shift(3);
        }

        internal function frame16():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame56():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame57():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.shift(4);
        }

        internal function frame59():*
        {
            this.shift(4);
        }

        internal function frame60():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_ll");
            this.self.playSound("ssf2_snd_sfx_dedede_smash");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-10),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            this.shift(4);
            this.shift(4);
        }

        internal function frame61():*
        {
            this.shift(3);
        }

        internal function frame62():*
        {
            this.self.updateAttackBoxStats(1, {
                "camShake":15,
                "damage":25,
                "hitStun":10,
                "selfHitStun":8,
                "effect_id":"effect_heavyHit",
                "direction":40,
                "power":50,
                "kbConstant":85,
                "effectSound":"ssf2_snd_sfx_dedede_hit_ll"
            });
            this.self.updateAttackBoxStats(2, {
                "camShake":15,
                "damage":25,
                "hitStun":10,
                "selfHitStun":8,
                "effect_id":"effect_heavyHit",
                "direction":40,
                "power":50,
                "kbConstant":85,
                "effectSound":"ssf2_snd_sfx_dedede_hit_ll"
            });
            this.self.updateAttackBoxStats(3, {
                "camShake":15,
                "damage":25,
                "hitStun":10,
                "selfHitStun":8,
                "effect_id":"effect_heavyHit",
                "direction":40,
                "power":50,
                "kbConstant":85,
                "effectSound":"ssf2_snd_sfx_dedede_hit_ll"
            });
        }

        internal function frame63():*
        {
            SSF2API.getCamera().shake(10);
            this.self.playSound("ssf2_snd_sfx_dedede_swing_land");
        }

        internal function frame64():*
        {
            this.self.updateAttackBoxStats(1, {
                "onlyAffectsGround":true,
                "damage":8,
                "direction":60,
                "power":100,
                "kbConstant":40,
                "hitStun":1,
                "selfHitStun":0,
                "effect_id":"effect_hit3",
                "effectSound":"dedede_hammerhitL",
                "camShake":0
            });
        }

        internal function frame67():*
        {
        }

        internal function frame75():*
        {
            this.shift(-4);
        }

        internal function frame78():*
        {
            this.shift(-4);
            this.shift(-4);
        }

        internal function frame80():*
        {
            this.shift(-4);
            this.shift(-4);
            this.shift(-4);
        }

        internal function frame82():*
        {
            this.shift(-5);
            this.self.endAttack();
        }


    }
}

