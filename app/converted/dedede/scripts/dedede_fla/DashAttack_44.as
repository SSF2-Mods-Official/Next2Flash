package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class DashAttack_44 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function DashAttack_44()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 6, this.frame7, 11, this.frame12, 12, this.frame13, 15, this.frame16, 23, this.frame24, 25, this.frame26, 33, this.frame34);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playSound("ssf2_snd_sfx_dedede_swing_l");
        }

        internal function frame4():*
        {
            this.self.setXSpeed(9, false);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame7():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_dashAtk");
        }

        internal function frame12():*
        {
            this.self.setXSpeed(8, false);
        }

        internal function frame13():*
        {
            SSF2API.getCamera().shake(6);
            this.self.setXSpeed(13, false);
            this.self.attachEffect("ground_bounce");
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_dashAtk_land");
            };
        }

        internal function frame16():*
        {
            this.self.updateAttackBoxStats(1, {
                "reversableAngle":false,
                "damage":13,
                "hitStun":5,
                "hitLag":-1,
                "selfHitStun":2,
                "effect_id":"effect_heavyHit",
                "direction":27,
                "power":35,
                "kbConstant":100,
                "effectSound":"ssf2_snd_sfx_dedede_hit_ll"
            });
        }

        internal function frame24():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
        }

        internal function frame26():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }


    }
}

