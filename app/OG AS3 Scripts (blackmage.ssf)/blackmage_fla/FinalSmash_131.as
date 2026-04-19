// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.FinalSmash_131

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;
    import flash.geom.*;
    import flash.display.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class FinalSmash_131 extends MovieClip 
    {

        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var warriorProj:*;
        public var thiefProj:*;
        public var wmageProj:*;
        public var fsTargets:Array;
        public var holy:Point;

        public function FinalSmash_131()
        {
            addFrameScript(0, this.frame1, 11, this.frame12, 14, this.frame15, 24, this.frame25, 25, this.frame26, 55, this.frame56, 84, this.frame85, 85, this.frame86, 115, this.frame116, 116, this.frame117);
        }

        public function checkFSTargets():void
        {
            if (((this.warriorProj.isDisposed()) && (this.thiefProj.isDisposed())))
            {
                this.self.stancePlayFrame("miss");
                this.self.destroyTimer(this.checkFSTargets);
            }
            else
            {
                if (this.fsTargets.length > 0)
                {
                    this.self.stancePlayFrame("whitemage");
                    this.self.destroyTimer(this.checkFSTargets);
                };
            };
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            this.warriorProj = null;
            this.thiefProj = null;
            this.wmageProj = null;
            this.fsTargets = new Array();
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.setGlobalVariable("fsTargets", this.fsTargets);
                this.self.unnattachFromGround();
            };
        }

        internal function frame12():*
        {
            SSF2API.getCamera().shake(10);
            this.self.playSound("bm_Warp_part2");
            this.warriorProj = this.self.fireProjectile("bm_fs_warrior");
            this.warriorProj.addToCamera();
            this.self.attachEffect("bm_fs_warp", {"x":this.self.flipX(-50)});
        }

        internal function frame15():*
        {
            SSF2API.getCamera().shake(10);
            this.self.playSound("bm_Warp_part2");
            this.thiefProj = this.self.fireProjectile("bm_fs_thief");
            this.thiefProj.addToCamera();
            this.self.attachEffect("bm_fs_warp", {"x":this.self.flipX(50)});
            this.self.createTimer(1, 0, this.checkFSTargets);
        }

        internal function frame25():*
        {
            this.self.stancePlayFrame("waitloop");
        }

        internal function frame26():*
        {
            SSF2API.getCamera().shake(10);
            this.self.playSound("bm_Warp_part2");
            this.wmageProj = this.self.fireProjectile("bm_fs_wmage");
            this.wmageProj.addToCamera();
            this.self.attachEffect("bm_fs_warp", {"x":this.self.flipX(80)});
        }

        internal function frame56():*
        {
            if (this.self.getCurrentProjectile() != null)
            {
                this.holy = new Point(this.self.getCurrentProjectile().getX(), this.self.getCurrentProjectile().getY());
                this.self.fireProjectile("bm_fs_flare", this.holy.x, (this.holy.y - 125), true);
            };
        }

        internal function frame85():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.resetMovement();
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame86():*
        {
            this.fsTargets = null;
            this.self.endAttack();
        }

        internal function frame116():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame117():*
        {
            this.fsTargets = null;
            this.self.endAttack();
        }


    }
}//package blackmage_fla

