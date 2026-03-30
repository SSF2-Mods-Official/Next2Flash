package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class FSmash_32 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var xframe:*;

        public function FSmash_32()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 42, this.frame43, 43, this.frame44, 46, this.frame47, 48, this.frame49, 51, this.frame52, 53, this.frame54, 67, this.frame68);
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

        internal function frame3():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame44():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.fireProjectile("chibi_fsmashProj");
        }

        internal function frame47():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame49():*
        {
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame52():*
        {
            this.self.updateAttackBoxStats(1, {
                "power":10,
                "hitLag":-1
            });
        }

        internal function frame54():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":9,
                "reversableAngle":true,
                "power":40,
                "weightKB":0,
                "kbConstant":130,
                "direction":40,
                "effect_id":"effect_elechit_heavy"
            });
            this.self.refreshAttackID();
        }

        internal function frame68():*
        {
            this.self.endAttack();
        }


    }
}

