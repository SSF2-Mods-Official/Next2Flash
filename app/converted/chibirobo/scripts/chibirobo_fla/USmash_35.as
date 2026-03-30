package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class USmash_35 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var xframe:*;

        public function USmash_35()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 44, this.frame45, 45, this.frame46, 47, this.frame48, 51, this.frame52, 66, this.frame67);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.xframe = null;
        }

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.playAttackSound(2);
            this.self.fireProjectile("chibi_usmashProj");
        }

        internal function frame48():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame52():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, {
                "stackKnockback":true,
                "direction":85,
                "weightKB":0,
                "damage":10,
                "power":50,
                "kbConstant":120,
                "effectSound":"brawl_zap_m",
                "effect_id":"effect_elechit_heavy"
            });
        }

        internal function frame67():*
        {
            this.self.endAttack();
        }


    }
}

