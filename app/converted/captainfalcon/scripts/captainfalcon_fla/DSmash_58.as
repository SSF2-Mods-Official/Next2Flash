package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class DSmash_58 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var xframe:String;

        public function DSmash_58()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 46, this.frame47, 47, this.frame48, 50, this.frame51, 51, this.frame52, 55, this.frame56, 56, this.frame57, 57, this.frame58, 65, this.frame66);
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
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.xframe = null;
        }

        internal function frame7():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame47():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame48():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame51():*
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.playSound("cfalcon_smashstart");
        }

        internal function frame52():*
        {
            this.self.playVoiceSound(1);
            this.self.playAttackSound(1);
            this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_dsmash", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame56():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":16,
                "direction":50,
                "power":40,
                "kbConstant":80
            });
        }

        internal function frame57():*
        {
            this.self.playSound("cfalcon_smashstart");
        }

        internal function frame58():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(-50),
                "y":-15,
                "parentLock":true
            });
            this.self.playAttackSound(1);
        }

        internal function frame66():*
        {
            this.self.endAttack();
        }


    }
}

